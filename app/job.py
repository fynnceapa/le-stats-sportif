from app.data_ingestor import DataIngestor
from queue import Queue
from app import webserver
from flask import jsonify
import pandas as pd
class Job:
    def __init__(self, job_id, question, status, data_ingestor):
        self.job_id = job_id
        self.question = question
        self.status = status
        self.data_ingestor = data_ingestor

    def do_job(self):
        # subclasses should implement this method
        pass

class JobStatesMean(Job):
    def __init__(self, job_id, question, status, data_ingestor):
        super().__init__(job_id, question, status, data_ingestor)
    def do_job(self):
        if self.question not in self.data_ingestor.questions_best_is_min and self.question not in self.data_ingestor.questions_best_is_max:
            return {"error": "Invalid question"}
        filtered_data = self.data_ingestor.data[self.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data[filtered_data['Year'] >= 2011]
        filtered_data = filtered_data[filtered_data['Year'] <= 2022]
        filtered_data = filtered_data.groupby('State')['Data_Value'].mean().reset_index()
        filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)
        return jsonify(filtered_data.to_dict(orient='records'))
    
class JobBest5(Job):
    def __init__(self, job_id, question, status, data_ingestor):
        super().__init__(job_id, question, status, data_ingestor)
    
    def do_job(self):
        if self.question not in self.data_ingestor.questions_best_is_min and self.question not in self.data_ingestor.questions_best_is_max:
            return {"error": "Invalid question"}
        filtered_data = self.data_ingestor.data[self.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data[filtered_data['Year'] >= 2011]
        filtered_data = filtered_data[filtered_data['Year'] <= 2022]
        filtered_data = filtered_data.groupby('State')['Data_Value'].mean().reset_index()
        filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)
        filtered_data = filtered_data.head(5)
        return jsonify(filtered_data.to_dict(orient='records'))
    
class JobWorst5(Job):
    def __init__(self, job_id, question, status, data_ingestor):
        super().__init__(job_id, question, status, data_ingestor)
    def do_job(self):
        if self.question not in self.data_ingestor.questions_best_is_min and self.question not in self.data_ingestor.questions_best_is_max:
            return {"error": "Invalid question"}
        filtered_data = self.data_ingestor.data[self.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data[filtered_data['Year'] >= 2011]
        filtered_data = filtered_data[filtered_data['Year'] <= 2022]
        filtered_data = filtered_data.groupby('State')['Data_Value'].mean().reset_index()
        filtered_data = filtered_data.sort_values(by='Data_Value', ascending=False)
        filtered_data = filtered_data.head(5)
        return jsonify(filtered_data.to_dict(orient='records'))