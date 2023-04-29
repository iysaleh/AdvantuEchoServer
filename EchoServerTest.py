
import pytest
import subprocess
import signal
import os
import string
import random
import time


'''
Pytest based test collection for unit & integration testing the EchoServer application.
'''
#Global Variables
SERVER_APP = "EchoServer.py"
CLIENT_APP = "EchoClient.py"
#See reset_test_artifacts() for how artifact names get set per test
SERVER_STDOUT_PATH = "test.echo_server.stdout"
SERVER_STDERR_PATH = "test.echo_server.stderr"
CLIENT_STDOUT_PATH = "test.echo_client.stdout"
CLIENT_STDERR_PATH = "test.echo_client.stderr"
SERVER_LOGFILE_PATH = "EchoServer.log"

#Environment variable to determine is test artifact cleanup occurs or not
KEEP_ARTIFACTS = os.environ.get("KEEP_ARTIFACTS", False)

#Helper Functions
"""Get a free port
    :return: free port number"""
def get_free_port():
    import socket
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port
"""Get a random string of specified length
    :param length: length of the string to be returned
    :return: random string of specified length
"""
def get_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

"""Get the contents of a file"""
def get_file_contents(path):
    #Must open with unicode encoding otherwise unicode string compares won't work.
    with open(path, 'r', encoding="utf-8") as f:
        return f.read()
    
"""Wait for the specified content to appear in the specified file
    :param path: path to the file to be read
    :param content: content to be searched for in the file
    :param timeout: time in seconds to wait for the content to appear in the file
    :return True if the content is found within the specified timeout
    :return False if the content is not found within the specified timeout
"""
def wait_for_content_in_file_with_timeout(path, content, timeout):
    start_time = time.time()
    while True:
        if content in get_file_contents(path):
            return True
        if time.time() - start_time > timeout:
            return False
        print("Waiting for \"%s\" in file: %s" % (content, path))
        

"""Get the standard echo test artifact contents as in memory strings"""
def get_standard_echo_test_artifact_contents():
    echo_server_stdout = get_file_contents(SERVER_STDOUT_PATH)
    echo_server_stderr = get_file_contents(SERVER_STDERR_PATH)
    echo_client_stdout = get_file_contents(CLIENT_STDOUT_PATH)
    echo_client_stderr = get_file_contents(CLIENT_STDERR_PATH)
    echo_server_log = get_file_contents(SERVER_LOGFILE_PATH)
    return echo_server_stdout, echo_server_stderr, echo_client_stdout, echo_client_stderr, echo_server_log


@pytest.fixture
def reset_test_artifact_names():
    global SERVER_STDOUT_PATH, SERVER_STDERR_PATH, CLIENT_STDOUT_PATH, CLIENT_STDERR_PATH, SERVER_LOGFILE_PATH
    test_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0].strip()
    SERVER_STDOUT_PATH = "test.%s.echo_server.stdout" % test_name
    SERVER_STDERR_PATH = "test.%s.echo_server.stderr" % test_name
    CLIENT_STDOUT_PATH = "test.%s.echo_client.stdout" % test_name
    CLIENT_STDERR_PATH = "test.%s.echo_client.stderr" % test_name
    SERVER_LOGFILE_PATH = "test.%s.EchoServer.log" % test_name

"""Test setup fixture - Start the server and client in separate processes.
    :return server: server process handle
    :return client: client process handle
"""
@pytest.fixture
def integration_test_setup(reset_test_artifact_names):
    port = get_free_port()
    # Start the server and client in separate processes, route all stdout/stderr streams to files.
    server_stdout = open(SERVER_STDOUT_PATH, "w")
    server_stderr = open(SERVER_STDERR_PATH, "w")
    client_stdout = open(CLIENT_STDOUT_PATH, "w")
    client_stderr = open(CLIENT_STDERR_PATH, "w")
    server = subprocess.Popen(['python', SERVER_APP, "--port", str(port),"--host","127.0.0.1", "--log_level", "DEBUG", "--log_file", SERVER_LOGFILE_PATH],shell=False,stdout=server_stdout, stderr=server_stderr,start_new_session=True)
    client = subprocess.Popen(['python', CLIENT_APP, "--port", str(port),"--host","127.0.0.1"],shell=True,stdin=subprocess.PIPE, stdout=client_stdout, stderr=client_stderr)
    yield server, client
    #Fixture teardown--
    #shutdown server & client apps
    server.send_signal(signal.SIGTERM)
    server.wait() #wait for full shutdown before continuing
    if(server):
        server.kill()
    client.send_signal(signal.SIGTERM)
    if(client):
        client.kill()
    client.wait()
    server_stdout.close()
    server_stderr.close()
    client_stdout.close()
    client_stderr.close()
    # Delete Test Log Artifacts if exists.
    if not KEEP_ARTIFACTS:
        if os.path.exists(SERVER_LOGFILE_PATH):
            os.remove(SERVER_LOGFILE_PATH)
        if os.path.exists(SERVER_STDOUT_PATH):
            os.remove(SERVER_STDOUT_PATH)
        if os.path.exists(SERVER_STDERR_PATH):
            os.remove(SERVER_STDERR_PATH)
        if os.path.exists(CLIENT_STDOUT_PATH):
            os.remove(CLIENT_STDOUT_PATH)
        if os.path.exists(CLIENT_STDERR_PATH):
            os.remove(CLIENT_STDERR_PATH)


def echo_and_check_procedure(client,echo_string):
    # Send a message to the server.
    client.communicate(echo_string.encode('utf-8'))
    # Read the response from the server.
    echo_worked = wait_for_content_in_file_with_timeout(CLIENT_STDOUT_PATH,echo_string, 5)
    if not echo_worked:
        pytest.fail("Echo did not work for string: "+echo_string)
    # Get the stdout/stderr content for each of the processes
    echo_server_stdout, echo_server_stderr, echo_client_stdout, echo_client_stderr, echo_server_log = get_standard_echo_test_artifact_contents()
    # Check that the response is the same as the message we sent.
    assert (echo_string) in echo_client_stdout
    # Check that the server log contains the message we sent.
    assert echo_string in echo_server_log

#End Helper Functions section. -------------------------------------------------------------------------------

#Integration Tests section.  ---------------------------------------------------------------------------------

"""Test the EchoServer application"""
def test_basic_end_to_end_integration(integration_test_setup):
    server, client = integration_test_setup
    echo_hello_string = "hello"
    echo_and_check_procedure(client,echo_hello_string)
def test_echo_unicode_string_integration(integration_test_setup):
    server, client = integration_test_setup
    echo_unicode_string = u"åäö"
    echo_and_check_procedure(client,echo_unicode_string)
def test_echo_maxlen_string_integration(integration_test_setup):
    server, client = integration_test_setup
    echo_max_length_string = "a" * 1024
    echo_and_check_procedure(client,echo_max_length_string)
def test_echo_maxlen_string_nl_integration(integration_test_setup):
    server, client = integration_test_setup
    echo_max_length_string_with_newline = "a" * 1024 + "\n"
    echo_and_check_procedure(client,echo_max_length_string_with_newline)
def test_echo_random_string_integration(integration_test_setup):
    server, client = integration_test_setup
    echo_random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=1024))
    echo_and_check_procedure(client,echo_random_string)

