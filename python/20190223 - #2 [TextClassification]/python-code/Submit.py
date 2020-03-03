import os
import time
import argparse
import numpy as np
import pandas as pd

from competitions.tools.timer import timer
from competitions.tools.DataReader import DataReader


def create_submission(X_train, y_train, X_test, df_test, thres, module):
    """
    train model with entire training data, predict test data,
    and create submission file

    Parameters
    ----------
    X_train, y_train, X_test: features and targets
    df_test: dataframe, test data
    thres: float, a decision threshold for classification
    module: a python module

    Return
    ------
    df_summission
    """
    model = module.get_model()
    print('Training model...')
    model = model.fit(X_train, y_train)
    # predict
    print('Predicting test...')
    y_pred = np.squeeze(model.predict_proba(X_test) > thres).astype('int')
    # create submission file
    return pd.DataFrame({'qid': df_test.qid, 'prediction': y_pred})


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Quora Insincere Questions Classification",
        description="Create Submission")
    parser.add_argument('--datapath', nargs='?', default=os.environ['DATA_PATH'],  # noqa
                        help='input data path')
    parser.add_argument('--model', nargs='?', default='model_v30',
                        help='model version')
    parser.add_argument('--thres', type=float, default=0.35,
                        help='decision threshold for classification')
    return parser.parse_args()


if __name__ == '__main__':
    # config
    # SHUFFLE = True
    # get args
    args = parse_args()
    datapath = args.datapath
    model = args.model
    best_thres = args.thres

    t0 = time.time()
    # 1. import module
    module = __import__(model)
    # 2. load and preprocess data
    with timer("Load and Preprocess"):
        dr = DataReader(os.path.join(datapath, 'quora', 'train.csv'), module, os.path.join(datapath, 'quora', 'test.csv'))
        df_train, X_train, df_test, X_test = dr.get_test()
    # 3. create submission file
    with timer('Trainning and Creating Submission'):
        filepath = os.path.join(datapath, 'submit_' + model + '.csv')
        df_submission = create_submission(
            X_train, df_train.target,
            X_test, df_test,
            best_thres, module)
        df_submission.to_csv(filepath, index=False)
        print('Save submission file to {}'.format(filepath))

    print('Entire program is done and it took {:.2f}s'.format(time.time() - t0))  # noqa
