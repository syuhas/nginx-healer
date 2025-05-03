import boto3
# def get_nginx_host_from_inventory(file='inventory.ini'):
#     with open(file) as f:
#         for line in f:
#             if line.startswith("nginx"):
#                 return line.split('=')[1].strip()
            

# server = get_nginx_host_from_inventory()
# print(server)

public_ip = '54.90.47.40'

def get_instance_id_from_ip(ip):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(
            Filters = [
                {
                    'Name': 'network-interface.association.public-ip',
                    'Values': [ip]
                }
            ]
        )
        if response['Reservations']:
            return response['Reservations'][0]['Instances'][0]['InstanceId']
        else:
            return None
    except Exception as e:
        print(f"Error retrieving instance ID: {e}")
        return None



ip = get_instance_id_from_ip(public_ip)

if ip: 
    print(f"Instance ID for IP {public_ip}: {ip}")
else:
    print(f"No instance found for IP {public_ip}")


# show me how a basic decorator works in python
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper



@my_decorator
def say_hello():
    print("Hello!")
say_hello()
# def retry(tries, delay):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             for i in range(tries):
#                 try:
#                     return func(*args, **kwargs)
#                 except Exception as e:
#                     logger.error(f'Attempt {i + 1} failed: {e}')
#                     time.sleep(delay)
#             raise Exception(f'All {tries} attempts failed.')
#         return wrapper
#     return decorator