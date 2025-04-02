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
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
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
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()

        if self.question in webserver.data_ingestor.questions_best_is_min:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)
        else:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=False)

        filtered_data = filtered_data.head(5)
        result = {}
        for index, row in filtered_data.iterrows():
            result[row['LocationDesc']] = row['Data_Value']
        return result

class JobWorst5(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)

    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()

        if self.question in webserver.data_ingestor.questions_best_is_min:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=False)
        else:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)

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
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data[filtered_data['LocationDesc'] == self.state]
        value = 0.0
        count = 0
        for index, row in filtered_data.iterrows():
            value += row['Data_Value']
            count += 1
        mean = value / count
        result = {}
        result[self.state] = mean
        return result

class JobGlobalMean(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)

    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        value = 0.0
        count = 0
        for index, row in filtered_data.iterrows():
            value += row['Data_Value']
            count += 1
        mean = value / count
        return {"global_mean": mean}

class JobStateMeanByCategory(Job):
    def __init__(self, job_id, question, state, status):
        super().__init__(job_id, question, status)
        self.state = state

    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            (webserver.data_ingestor.data['Question'] == self.question) &
            (webserver.data_ingestor.data['LocationDesc'] == self.state)
        ]

        stratification_means = (
            filtered_data
            .groupby(['StratificationCategory1', 'Stratification1'])['Data_Value']
            .mean()
            .to_dict()
        )

        formatted_means = {str(k): v for k, v in stratification_means.items()}

        return {self.state: formatted_means}
    
class JobStateDiffFromMean(Job):
    def __init__(self, job_id, question, state, status):
        super().__init__(job_id, question, status)
        self.state = state

    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        global_mean = filtered_data['Data_Value'].mean()
        filtered_data = filtered_data[filtered_data['LocationDesc'] == self.state]
        state_mean = filtered_data['Data_Value'].mean()
        diff = global_mean - state_mean
        result = {}
        result[self.state] = diff
        return result

class JobDiffFromMean(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)

    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        global_mean = filtered_data['Data_Value'].mean()
        state_means = {}
        for state in filtered_data['LocationDesc']:
            state_data = filtered_data[filtered_data['LocationDesc'] == state]
            state_mean = state_data['Data_Value'].mean()
            state_means[state] = state_mean
        diff_from_mean = {}
        for state, mean in state_means.items():
            diff_from_mean[state] = global_mean - mean
        return diff_from_mean

class JobMeanByCategory(Job):
    def __init__(self, job_id, question, status):
        super().__init__(job_id, question, status)

    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        
        stratification_means = (
            filtered_data
            .groupby(['LocationDesc', 'StratificationCategory1', 'Stratification1'])['Data_Value']
            .mean()
            .to_dict()
        )
        
        formatted_means = {
            str((state, stratification_category, stratification)): v
            for (state, stratification_category, stratification), v in stratification_means.items()
        }
        
        return formatted_means

