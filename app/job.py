from queue import Queue
from flask import jsonify
import pandas as pd
from app import webserver

class Job:
    def __init__(self, job_id, question, status):
        self.job_id = job_id
        self.question = question
        self.status = status

    def do_job(self):
        # subclasses should implement this method
        pass

class JobStatesMean(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)
    def do_job(self):
        state_means = {}
        filtered_data = webserver.data_ingestor.data[webserver.data_ingestor.data['Question'] == self.question]
        for state in filtered_data['LocationDesc']:
            state_data = filtered_data[filtered_data['LocationDesc'] == state]
            state_mean = state_data['Data_Value'].mean()
            state_means[state] = state_mean
        sorted_states = sorted(state_means.items(), key=lambda x: x[1])
        result = {}
        for state, mean in sorted_states:
            result[state] = mean
        return result
    
class JobBest5(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)
    
    def do_job(self):
        filtered_data = webserver.data_ingestor.data[webserver.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()
        filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)
        filtered_data = filtered_data.head(5)
        result = {}
        for index, row in filtered_data.iterrows():
            result[row['LocationDesc']] = row['Data_Value']
        return result
    
class JobWorst5(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)
    def do_job(self):
        filtered_data = webserver.data_ingestor.data[webserver.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()
        filtered_data = filtered_data.sort_values(by='Data_Value', ascending=False)
        filtered_data = filtered_data.head(5)
        result = {}
        for index, row in filtered_data.iterrows():
            result[row['LocationDesc']] = row['Data_Value']
        return result

class JobStateMean(Job):
    def __init__(self, job_id, question, state, status):
        super().__init__(job_id, question, status)
        self.state = state
    def do_job(self):
        filtered_data = webserver.data_ingestor.data[webserver.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data[filtered_data['LocationDesc'] == self.state]
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()
        filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)
        value = 0
        count = 0
        for index, row in filtered_data.iterrows():
            value += row['Data_Value']
            count += 1
        if count == 0:
            return {"error": "No data found"}
        mean = value / count
        return {self.state, mean}
    
class JobGlobalMean(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)
    def do_job(self):
        value = 0
        count = 0
        question = self.question
        filtered_data = webserver.data_ingestor.data[webserver.data_ingestor.data['Question'] == question]
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()
        filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)
        for index, row in filtered_data.iterrows():
            value += row['Data_Value']
            count += 1
        if count == 0:
            return {"error": "No data found"}
        mean = value / count
        return {"global_mean", mean}