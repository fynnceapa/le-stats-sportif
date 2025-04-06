from app import webserver

class Job: # pylint: disable=too-few-public-methods
    """Base class for jobs. Every job inherits this class and implements the do_job method."""
    def __init__(self, job_id, question, status):
        self.job_id = job_id
        self.question = question
        self.status = status

    def do_job(self):
        """subclasses should implement this method"""
        pass

class JobStatesMean(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the mean of a question for each state."""
    def do_job(self):
        state_means = {}

        # Get the data for the specific question
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]

        # group by each state n get the mean
        for state in filtered_data['LocationDesc']:
            state_data = filtered_data[filtered_data['LocationDesc'] == state]
            state_mean = state_data['Data_Value'].mean()
            state_means[state] = state_mean

        # get the mean for each state in a dictionary so it can be jsonified later
        result = {}
        for state, mean in state_means.items():
            result[state] = mean
        return result

class JobBest5(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the best 5 states for a question"""
    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        
        # group by each state n get the mean
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()

        # check the type of question so the data can be sorted
        if self.question in webserver.data_ingestor.questions_best_is_min:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)
        else:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=False)

        filtered_data = filtered_data.head(5)


        result = {}
        # intertuples is used to get the data in a dictionary format
        for row in filtered_data.itertuples(index=False):
            result[row.LocationDesc] = row.Data_Value
        return result

class JobWorst5(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the worst 5 states for a question"""
    def do_job(self):
        # basically the same as best5
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        filtered_data = filtered_data.groupby('LocationDesc')['Data_Value'].mean().reset_index()

        if self.question in webserver.data_ingestor.questions_best_is_min:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=False)
        else:
            filtered_data = filtered_data.sort_values(by='Data_Value', ascending=True)

        filtered_data = filtered_data.head(5)
        result = {}
        for row in filtered_data.itertuples(index=False):
            result[row.LocationDesc] = row.Data_Value
        return result

class JobStateMean(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the mean of a question for a specific state."""
    def __init__(self, job_id, question, state, status):
        super().__init__(job_id, question, status)
        self.state = state

    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]
        # i get the data for the specific state
        filtered_data = filtered_data[filtered_data['LocationDesc'] == self.state]

        # i get the mean for the specific state
        mean = filtered_data['Data_Value'].mean()

        return {self.state: mean}

class JobGlobalMean(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the global mean of a question."""
    def do_job(self):
        filtered_data = webserver.data_ingestor.data[
            webserver.data_ingestor.data['Question'] == self.question]

        # get the mean for the specific question
        mean = filtered_data['Data_Value'].mean()

        return {"global_mean": mean}

class JobStateMeanByCategory(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the mean of a question for a specific state and stratification category."""
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

class JobStateDiffFromMean(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the difference between the global mean and the state mean for a question"""
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

class JobDiffFromMean(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the difference between the global mean and the state means for a question."""
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

class JobMeanByCategory(Job): # pylint: disable=too-few-public-methods
    """Job to calculate the mean of a question for each state and stratification category."""
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
