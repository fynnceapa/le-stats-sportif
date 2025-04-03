import os
import json
from app import webserver
from app import job
from flask import request, jsonify
from threading import Lock

lock = Lock()

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    """Example POST endpoint that receives JSON data."""
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)
        # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """gets the result of a job"""
    if webserver.job_counter < int(job_id):
        webserver.logger.error(f"Job {job_id} does not exist")

        return jsonify({
            'status': 'error',
            'reason': 'Invalid job_id'
        })

    result_path = os.path.join('results', f'{job_id}.json')
    if os.path.exists(result_path) and webserver.job_statuses[int(job_id)] == 'done':
        with open(result_path, 'r') as f:
            result = json.load(f)

        webserver.logger.info(f"Job {job_id} finished, returning result with code 200")

        return jsonify({'status': 'done', 'data': result})

    webserver.logger.info(f"Job {job_id} is still running, cannot return result")

    return jsonify({'status': 'running'})

@webserver.route('/api/jobs', methods=['GET'])
def get_jobs():
    """gets the status of all jobs"""
    jobs = []
    for job_id in range(webserver.job_counter):
        if job_id in webserver.job_statuses:
            status = webserver.job_statuses[job_id]
            jobs.append({f"job_id_{job_id}": status})
    webserver.logger.info(f"Returning job statuses: {jobs}")
    return jsonify({'status': 'done','data': jobs})

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    """gracefully shuts down the server"""
    webserver.logger.info("Received shutdown request")
    webserver.shutdown_event.set()
    webserver.task_runner.shutdown()

    if webserver.job_queue().empty():
        return jsonify({'status': 'done'})
    else:
        return jsonify({"status": 'running',})

@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs():
    """returns the number of jobs in the queue"""
    num_jobs = webserver.job_queue.qsize()
    webserver.logger.info(f"Number of jobs in the queue: {num_jobs}")
    return jsonify({"num_jobs": num_jobs})

def add_job(job_type, data):
    """adds a job to the queue in threadpool"""
    if webserver.shutdown_event.is_set():
        webserver.logger.error("Server is down, cannot add new jobs")
        return -2

    job_id = 0
    with lock:
        job_id = webserver.job_counter
        webserver.job_counter += 1

    webserver.logger.info(f"Job {job_id} is being added to "
                          f"the queue: {job_type} for question: {data['question']}")

    if job_type == 'best5':
        jobb = job.JobBest5(job_id, data['question'], 'running')
    elif job_type == 'worst5':
        jobb = job.JobWorst5(job_id, data['question'], 'running')
    elif job_type == 'states_mean':
        jobb = job.JobStatesMean(job_id, data['question'], 'running')
    elif job_type == 'state_mean':
        jobb = job.JobStateMean(job_id, data['question'], data['state'], 'running')
    elif job_type == 'global_mean':
        jobb = job.JobGlobalMean(job_id, data['question'], 'running')
    elif job_type == 'state_mean_by_category':
        jobb = job.JobStateMeanByCategory(job_id, data['question'], data['state'], 'running')
    elif job_type == 'state_diff_from_mean':
        jobb = job.JobStateDiffFromMean(job_id, data['question'], data['state'], 'running')
    elif job_type == 'diff_from_mean':
        jobb = job.JobDiffFromMean(job_id, data['question'], 'running')
    elif job_type == 'mean_by_category':
        jobb = job.JobMeanByCategory(job_id, data['question'], 'running')
    else:
        webserver.logger.error(f"Job {job_id} has an invalid job type: {job_type}")
        with webserver.counter_lock:
            webserver.job_counter -= 1
        return -1

    webserver.job_queue.put(jobb)
    webserver.job_statuses[job_id] = 'running'
    return job_id

def check_add_job_return(i):
    """checks the return value of add_job and returns the appropriate response"""
    if i == -1:
        return jsonify({
            'status': 'error',
            'reason': 'invalid job type'
        })
    elif i == -2:
        return jsonify({
            'status': 'error',
            'reason': 'shutting down'
        })
    else:
        return jsonify({"job_id": i})

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """gets the mean of a question for all states"""
    request_data = request.json
    i = add_job('states_mean', request_data)
    return check_add_job_return(i)

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """gets the mean of a question for a specific state"""
    request_data = request.json
    i = add_job('state_mean', request_data)
    return check_add_job_return(i)

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """gets the best 5 states for a question"""
    request_data = request.json
    i = add_job('best5', request_data)
    return check_add_job_return(i)

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """gets the worst 5 states for a question"""
    request_data = request.json
    i = add_job('worst5', request_data)
    return check_add_job_return(i)

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """gets the global mean of a question"""
    request_data = request.json
    i = add_job('global_mean', request_data)
    return check_add_job_return(i)

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """gets the difference from the mean of a question"""
    request_data = request.json
    i = add_job('diff_from_mean', request_data)
    return check_add_job_return(i)

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """gets the difference from the mean of a question for a specific state"""
    request_data = request.json
    i = add_job('state_diff_from_mean', request_data)
    return check_add_job_return(i)

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """gets the mean of a question for a specific state and stratification category"""
    request_data = request.json
    i = add_job('mean_by_category', request_data)
    return check_add_job_return(i)

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """gets the mean of a question for a specific state and stratification category"""
    request_data = request.json
    i = add_job('state_mean_by_category', request_data)
    return check_add_job_return(i)

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    """Main page of the web server."""
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    """Get the defined routes in the web server."""
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
