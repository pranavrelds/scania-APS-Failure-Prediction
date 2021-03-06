from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics  import roc_auc_score,accuracy_score

class ModelFinder:
    """
    This class helps to find the model with best accuracy and AUC score.

    """
    def __init__(self,file_object,logger_object):
        self.file_object = file_object
        self.logger_object = logger_object
        self.sv_classifier=SVC()
        self.knn = KNeighborsClassifier()

    def get_best_params_for_svm(self,train_x,train_y):
        """
        Method Name: get_best_params_for_naive_bayes
        Description: get the parameters for the SVM Algorithm which gives the best accuracy using Hyper Parameter Tuning
        Output: The model with the best parameters
        """
        self.logger_object.log(self.file_object, 'Entered the get_best_params_for_svm method of the ModelFinder class')
        try:
            # initializing with different combination of parameters
            self.param_grid = {"kernel": ['rbf', 'sigmoid'],
                                "C": [0.1, 0.5, 1.0]}

            #Creating an object of the Grid Search class
            self.grid = GridSearchCV(estimator=self.sv_classifier, param_grid=self.param_grid, cv=5,  verbose=3)

            #finding the best parameters
            self.grid.fit(train_x, train_y)

            #extracting the best parameters
            self.kernel = self.grid.best_params_['kernel']
            self.C = self.grid.best_params_['C']


            #creating a new model with the best parameters
            self.sv_classifier = SVC(kernel=self.kernel,C=self.C,random_state=0)

            # training the new model
            self.sv_classifier.fit(train_x, train_y)
            self.logger_object.log(self.file_object,'SVM best params: '+str(self.grid.best_params_)+'. Exited the get_best_params_for_svm method of the ModelFinder class')

            return self.sv_classifier

        except Exception as e:
            self.logger_object.log(self.file_object,'Exception occured in get_best_params_for_svm method of the ModelFinder class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,'SVM training  failed. Exited the get_best_params_for_svm method of the ModelFinder class')
            raise Exception()

    def get_best_params_for_KNN(self, train_x, train_y):
        """
        Method Name: get_best_params_for_KNN
        Description: get the parameters for KNN Algorithm which give the best accuracy using Hyper Parameter Tuning
        Output: The model with the best parameters

        """
        self.logger_object.log(self.file_object,'Entered the get_best_params_for_Ensembled_KNN method of the ModelFinder class')
        try:
            # initializing with different combination of parameters
            self.param_grid_knn = {
                'algorithm': ['ball_tree', 'kd_tree'],
                'leaf_size': [10, 17, 24, 28, 30, 35],
                'n_neighbors': [4, 5, 8, 10, 11],
                'p': [1, 2]
            }

            # Creating an object of the Grid Search class
            self.grid = GridSearchCV(self.knn, self.param_grid_knn, verbose=3, cv=4)
            # finding the best parameters
            self.grid.fit(train_x, train_y)

            # extracting the best parameters
            self.algorithm = self.grid.best_params_['algorithm']
            self.leaf_size = self.grid.best_params_['leaf_size']
            self.n_neighbors = self.grid.best_params_['n_neighbors']
            self.p = self.grid.best_params_['p']

            # creating a new model with the best parameters
            self.knn = KNeighborsClassifier(algorithm=self.algorithm, leaf_size=self.leaf_size, n_neighbors=self.n_neighbors, p=self.p, n_jobs=-1)

            # training the new model
            self.knn.fit(train_x, train_y)
            self.logger_object.log(self.file_object,'KNN best params: ' + str(self.grid.best_params_) + '. Exited the KNN method of the ModelFinder class')
            return self.knn

        except Exception as e:
            self.logger_object.log(self.file_object,'Exception occured in knn method of the ModelFinder class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,'knn Parameter tuning  failed. Exited the knn method of the ModelFinder class')
            raise Exception()

    def get_best_model(self,train_x,train_y,test_x,test_y):
        """
        Method Name: get_best_model
        Description: Find out the Model which has the best AUC score.
        Output: The best model name and the model object

        """
        self.logger_object.log(self.file_object, 'Entered the get_best_model method of the ModelFinder class')
        try:
            self.knn= self.get_best_params_for_KNN(train_x,train_y)
            self.prediction_knn = self.knn.predict(test_x) # Predictions using the KNN Model

            if len(test_y.unique()) == 1: #if there is only one label in y, then roc_auc_score returns error. Use accuracy in that case
                self.knn_score = accuracy_score(test_y, self.prediction_knn)
                self.logger_object.log(self.file_object, 'Accuracy for KNN:' + str(self.knn_score))  # Log AUC
            else:
                self.knn_score = roc_auc_score(test_y, self.prediction_knn) # AUC for KNN
                self.logger_object.log(self.file_object, 'AUC for KNN:' + str(self.knn_score)) # Log AUC

            # create best model for SVM
            self.svm=self.get_best_params_for_svm(train_x,train_y)
            self.prediction_svm=self.svm.predict(test_x) # Prediction using the SVM Algorithm

            if len(test_y.unique()) == 1:#if there is only one label in y, then roc_auc_score returns error. Use accuracy in that case
                self.svm_score = accuracy_score(test_y,self.prediction_svm)
                self.logger_object.log(self.file_object, 'Accuracy for SVM:' + str(self.svm_score))
            else:
                self.svm_score = roc_auc_score(test_y, self.prediction_svm) # AUC for Random Forest
                self.logger_object.log(self.file_object, 'AUC for SVM:' + str(self.svm_score))

            #comparing the two models
            if(self.svm_score <  self.knn_score):
                return 'KNN',self.knn
            else:
                return 'SVM',self.sv_classifier

        except Exception as e:
            self.logger_object.log(self.file_object,'Exception occured in get_best_model method of the ModelFinder class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,'Model Selection Failed. Exited the get_best_model method of the ModelFinder class')
            raise Exception()

