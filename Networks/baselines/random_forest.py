from __future__ import print_function

from data_loader import *
import argparse
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from util import output_classification_result, reshape_data_into_2_dim


class RandomForestClassification:
    def __init__(self, conf):
        self.conf = conf
        self.max_features = conf['max_features']
        self.n_estimators = conf['n_estimators']
        self.min_samples_leaf = conf['min_samples_leaf']
        self.class_weight = conf['class_weight']
        self.EF_ratio_list = conf['enrichment_factor']['ratio_list']
        self.random_seed = conf['random_seed']

        if 'hit_ratio' in self.conf.keys():
            self.hit_ratio = conf['hit_ratio']
        else:
            self.hit_ratio = 0.01
        np.random.seed(seed=self.random_seed)
        return

    def setup_model(self):
        model = RandomForestClassifier(n_estimators=self.n_estimators,
                                       max_features=self.max_features,
                                       min_samples_leaf=self.min_samples_leaf,
                                       n_jobs=8,
                                       class_weight=self.class_weight,
                                       random_state=self.random_seed,
                                       oob_score=False,
                                       verbose=1)
        return model

    def train_and_predict(self, X_train, y_train, X_test, y_test, weight_file):
        model = self.setup_model()
        model.fit(X_train, y_train)

        y_pred_on_train = reshape_data_into_2_dim(model.predict(X_train))
        if X_test is not None:
            y_pred_on_test = reshape_data_into_2_dim(model.predict(X_test))
        else:
            y_pred_on_test = None

        output_classification_result(y_train=y_train, y_pred_on_train=y_pred_on_train,
                                     y_val=None, y_pred_on_val=None,
                                     y_test=y_test, y_pred_on_test=y_pred_on_test)

        self.save_model(model, weight_file)

        return

    def predict_with_existing(self, X_data, weight_file):
        model = self.load_model(weight_file)
        y_pred = reshape_data_into_2_dim(model.predict_proba(X_data)[:, 1])
        return y_pred

    def eval_with_existing(self, X_train, y_train, X_test, y_test, weight_file):
        model = self.load_model(weight_file)

        y_pred_on_train = reshape_data_into_2_dim(model.predict(X_train))
        if X_test is not None:
            y_pred_on_test = reshape_data_into_2_dim(model.predict(X_test))
        else:
            y_pred_on_test = None

        output_classification_result(y_train=y_train, y_pred_on_train=y_pred_on_train,
                                     y_val=None, y_pred_on_val=None,
                                     y_test=y_test, y_pred_on_test=y_pred_on_test)

        return

    def save_model(self, model, weight_file):
        from sklearn.externals import joblib
        joblib.dump(model, weight_file, compress=3)
        return

    def load_model(self, weight_file):
        from sklearn.externals import joblib
        model = joblib.load(weight_file)
        return model


def demo_random_forest_classification():
    conf = {
        'max_features': 'log2',
        'n_estimators': 4000,
        'min_samples_leaf': 1,
        'class_weight': 'balanced',
        'enrichment_factor': {
            'ratio_list': [0.02, 0.01, 0.0015, 0.001]
        },
        'random_seed': 1337
    }

    idx_list = load_index(number_of_class, index)
    [train_smiles_list, train_label_list], [test_smiles_list, test_label_list] = index2smiles(idx_list, number_of_class)
    train_fps_list, test_fps_list = smiles2fps(train_smiles_list), smiles2fps(test_smiles_list)
    print(train_fps_list.shape, '\t', train_label_list.shape)
    print(test_fps_list.shape, '\t', test_label_list.shape)
    X_train, y_train, X_test, y_test = train_fps_list, train_label_list, test_fps_list, test_label_list

    task = RandomForestClassification(conf=conf)
    task.train_and_predict(X_train, y_train, X_test, y_test, weight_file)
    task.eval_with_existing(X_train, y_train, X_test, y_test, weight_file)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weight_file', dest='weight_file', required=True)
    parser.add_argument('--number_of_class', type=int, dest='number_of_class', default=3, required=False)
    parser.add_argument('--index', type=int, dest='index', default=1, required=False)
    given_args = parser.parse_args()
    weight_file = given_args.weight_file
    number_of_class = given_args.number_of_class
    index = given_args.index

    demo_random_forest_classification()
