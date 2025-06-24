import pandas as pd;
import json;
import pickle;
from flask import request, jsonify;
from flask_restful import Resource;
from CropMaster import db;
from CropMaster.models import ResultOfUsers, User;
from flask_login import current_user;


# *******

# *********
class PredictionAPI(Resource):
    def post(self):
        predicted_value = None
        data = request.get_json()
        array_json = []
        array_json.append(data)

        # Load scaler and columns only ONCE (outside function)
        with open('CropMaster/models/std_scaler_for_distance_based.pkl', 'rb') as f:
            scaler = pickle.load(f)

        with open('CropMaster/models/train_columns.pkl', 'rb') as f:
            train_columns = pickle.load(f)

        with open('CropMaster/models/ensemble_model.pkl', 'rb') as f:
            ensemble = pickle.load(f)

        # Transform function using preloaded files
        def transform_X_test(X_test):
            columns_to_encode = ['state', 'district', 'crop', 'season']
            columns_to_scale = ['area', 'rainfall', 'avg_temp']

            X_test_encoded = pd.get_dummies(X_test, columns=columns_to_encode, drop_first=True)
            X_test_encoded = X_test_encoded.reindex(columns=train_columns, fill_value=0)
            X_test_encoded[columns_to_scale] = scaler.transform(X_test_encoded[columns_to_scale])

            return X_test_encoded

        # Prediction function
        def get_prediction_from_json(array_json):
            X_test = pd.DataFrame(json.loads(array_json))
            X_test_transformed = transform_X_test(X_test)
            prediction = max(ensemble.predict(X_test_transformed), 0)
            return {"prediction": float(prediction[0]).__round__(2)}

        # Final call (example)
        predicted_value = get_prediction_from_json(json.dumps(array_json))


        if predicted_value:
            if data.get("user_auth_id")[0]:
                print("test-1")
                result = ResultOfUsers(user_id=int(data.get("user_auth_id")[1]), state=data.get("state"), district=data.get("district"), season=data.get("season"), average_temp=float(data.get("avg_temp")), average_rainfall=float(data.get("rainfall")), crop=str(data.get("crop")), predicted_amount=predicted_value["prediction"])
                db.session.add(result)
                db.session.commit()
                print("test-2")
                return jsonify({"message": "current user is logged in and we've stored the prediction", "result": predicted_value, "status_code":201})
            else:
                print(predicted_value)
                return jsonify({"message":"current user is not logged so we won't store the data in the database", "result": predicted_value, "status_code":200})        
        else:
            return jsonify({"message":"predicted value of crop production is none", "result": None ,"status_code": 200})