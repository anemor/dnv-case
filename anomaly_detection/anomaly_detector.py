import os
import time
from datetime import datetime
import pandas as pd

from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.ai.anomalydetector.models import DetectionRequest, ModelInfo
from azure.ai.anomalydetector.models import ModelStatus, DetectionStatus
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


#token_credential = DefaultAzureCredential()

subscription_key = "1c976565fa5645a18d6dc0317745b05a"
anomaly_detector_endpoint = "https://dnv-anomali-detector.cognitiveservices.azure.com/"

class MultivariateSample():
    def __init__(self, subscription_key, anomaly_detector_endpoint, data_source=None):
        self.sub_key = subscription_key
        self.end_point = anomaly_detector_endpoint

        # Create an Anomaly Detector client

        # <client>
        self.ad_client = AnomalyDetectorClient(AzureKeyCredential(self.sub_key), self.end_point)
        # </client>

        self.data_source = "https://mathiasotnes.blob.core.windows.net/newcontainer/bastoI.zip?sp=r&st=2022-10-22T22:43:56Z&se=2022-10-23T06:43:56Z&spr=https&sv=2021-06-08&sr=b&sig=4JE0IZC5v%2BMAipq%2Bh3yNUsSEF2Lhrp2nBx3IWAmY3As%3D"

    def train(self, start_time, end_time):
        # Number of models available now
        model_list = list(self.ad_client.list_multivariate_model(skip=0, top=10000))
        print("{:d} available models before training.".format(len(model_list)))
        
        # Use sample data to train the model
        # slidingWindow should be 1-3 periodes. 1 period is 120, and default slidingWindow is 300
        print("Training new model...(it may take a few minutes)")
        data_feed = ModelInfo(start_time=start_time, end_time=end_time, source=self.data_source)
        response_header = \
        self.ad_client.train_multivariate_model(data_feed, cls=lambda *args: [args[i] for i in range(len(args))])[-1]
        trained_model_id = response_header['Location'].split("/")[-1]
        
        # Model list after training
        new_model_list = list(self.ad_client.list_multivariate_model(skip=0, top=10000))
        
        # Wait until the model is ready. It usually takes several minutes
        model_status = None
        while model_status != ModelStatus.READY and model_status != ModelStatus.FAILED:
            model_info = self.ad_client.get_multivariate_model(trained_model_id).model_info
            model_status = model_info.status
            print(model_status)
            time.sleep(10)

        if model_status == ModelStatus.FAILED:
            print("Creating model failed.")
            print("Errors:")
            if model_info.errors:
                for error in model_info.errors:
                    print("Error code: {}. Message: {}".format(error.code, error.message))
            else:
                print("None")
            return None

        if model_status == ModelStatus.READY:
            # Model list after training
            new_model_list = list(self.ad_client.list_multivariate_model(skip=0, top=10000))
            print("Done.\n--------------------")
            print("{:d} available models after training.".format(len(new_model_list)))

        # Return the latest model id
        return trained_model_id

    def detect(self, model_id, start_time, end_time):
        # Detect anomaly in the same data source (but a different interval)
        try:
            detection_req = DetectionRequest(source=self.data_source, start_time=start_time, end_time=end_time)
            response_header = self.ad_client.detect_anomaly(model_id, detection_req,
                                                            cls=lambda *args: [args[i] for i in range(len(args))])[-1]
            result_id = response_header['Location'].split("/")[-1]
        
            # Get results (may need a few seconds)
            r = self.ad_client.get_detection_result(result_id)
            while r.summary.status != DetectionStatus.READY and r.summary.status != DetectionStatus.FAILED:
                r = self.ad_client.get_detection_result(result_id)
                time.sleep(2)

            if r.summary.status == DetectionStatus.FAILED:
                print("Detection failed.")
                print("Errors:")
                if r.summary.errors:
                    for error in r.summary.errors:
                        print("Error code: {}. Message: {}".format(error.code, error.message))
                else:
                    print("None")
                return None
        except HttpResponseError as e:
            print('Error code: {}'.format(e.error.code), 'Error message: {}'.format(e.error.message))
        except Exception as e:
            raise e
        return r
    
    def export_model(self, model_id, model_path="model.zip"):
    
        # Export the model
        model_stream_generator = self.ad_client.export_model(model_id)
        with open(model_path, "wb") as f_obj:
            while True:
                try:
                    f_obj.write(next(model_stream_generator))
                except StopIteration:
                    break
                except Exception as e:
                    raise e
    def delete_model(self, model_id):
    
        # Delete the model
        self.ad_client.delete_multivariate_model(model_id)
        model_list_after_delete = list(self.ad_client.list_multivariate_model(skip=0, top=10000))
        print("{:d} available models after deletion.".format(len(model_list_after_delete)))


if __name__ == '__main__':
    subscription_key = "1c976565fa5645a18d6dc0317745b05a"
    anomaly_detector_endpoint = "https://dnv-anomali-detector.cognitiveservices.azure.com/"

    # Create a new sample and client
    sample = MultivariateSample(subscription_key, anomaly_detector_endpoint, data_source=None)
    model_list = list(sample.ad_client.list_multivariate_model(skip=0, top=10000))

    # Deleting model list
    #for model in model_list:
    #    sample.delete_model(model.model_id)

    # Train a new model 2022-08-07 16:35:00
    model_id = sample.train(datetime(2022, 8, 1, 7, 21, 0), datetime(2022, 8, 7, 16, 35, 0))
    print("Model ID:\t", model_id)
    #model_id = '6a33e36c-524e-11ed-ad83-466e37c3b7ef'

    # Reference
    result = sample.detect(model_id, datetime(2022, 8, 8, 0, 0, 0), datetime(2022, 8, 9, 0, 0, 0))
    print("Result ID:\t", result.result_id)
    print("Result summary:\t", result.summary)
    print("Result length:\t", len(result.results))

    # Writing result to csv-file
    dataDict = {'timestamp': [], 'value': []}
    for datapoint in result.results:
        dataDict["timestamp"].append(datapoint.timestamp)
        dataDict["value"].append(datapoint.value.is_anomaly)
    df = pd.DataFrame(dataDict)
    df.to_csv('anomalies.csv', index=False)

    # Export model 
    sample.export_model(model_id, "model.zip")

    # Delete model
    #sample.delete_model(model_id)
    