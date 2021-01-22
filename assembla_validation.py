#Requirement:
#make a creds_personal file for ticket access having access_key & access_secret
import json
from creds_personal import access_key, access_secret
from assembla import API,Ticket
import requests
from pprint import pprint
import re
import time

assembla_data = {}
app_names = {}
attachements = {}
def assembla_data_to_json( my_space, my_headers, drop2_tickets, drop3_tickets, drop4_tickets):
	ticket_ls = []
	count = 0
	
		for ticket in user.tickets():
			attachment_list_json = []
			attachments_temp = []
			attachement_names = []
			# print(ticket)
			if ticket['status'] == 'Pcap Checks' or ticket['status'] == 'Pcap Done' or ticket['status'] == 'XML Done':
				if ticket['custom_fields']['SaaS Validity'] == 'Yes' or ticket['custom_fields']['SaaS Validity'] == ' ':
					# if (not ticket['number'] in drop1_tickets) and (ticket['number'] in drop2_tickets):
					# if (not ticket['number'] in drop2_tickets) and (not ticket['number'] in drop3_tickets) :
					if ticket['number'] in drop4_tickets:
						count += 1
						
						ticket_number = ticket['number']
						# if ticket['status'] == ''
						ticket_ls.append(ticket_number)
						# print(ticket_number)
						# get attachements list through assembla api
						print("Fetching Assembla data.. Please wait...")
						space_name = "Granular-Controls"
						api = f'https://api.assembla.com/v1/spaces/{space_name}/tickets/{ticket_number}/attachments.json'
						# print(api)
						attachment_api_get = api	
						api_response = requests.get(attachment_api_get, headers=my_headers)
						response = api_response.text
						
						if len(response) > 0: 
							attachment_list_json = json.loads(api_response.text)
							for attachment in attachment_list_json:
								name = attachment['name'].split('.')
								# print(name)
								if name[-1] == 'pcap' or name[-1] == 'PCAP':
									attachments_temp.append(attachment_list_json)
									attachement_names.append(attachment['name'])
						else:
							attachement_names.append("Not found")
					
						# get assembla data through assembla wrapper 
						assembla_data[ticket['summary']] = { 'Assigned to':user_name, 'Ticket_number': ticket_number, 'Status': ticket['status'] ,'custom_fields': ticket['custom_fields'], 'Attachments_count': len(attachments_temp), 'Attachments_list':	attachement_names }
						# if ticket['status'] == 'Request for Info':
						# 	if len(attachment_list_json) >= 5:
						# 		app_names[ticket['summary']] = { 'Assigned to':user_name, 'Status': ticket['status'], 'Attachments_count': len(attachment_list_json)}
						attachements[ticket['summary']] = {'Assigned to':user_name, 'Attachments': attachement_names}

		# writing it to json file
		with open('available_tickets_drop4.json', 'w') as fp:  
			json.dump(ticket_ls,fp, indent = 1)

		print(count)
		# writing it to json file
		with open('assembla_data', 'w') as fp:  
			json.dump(assembla_data,fp,indent=1)

		# writing it to json file
		with open('attachments_pcaps', 'w') as fp:  
			json.dump(attachements,fp,indent=1)

def initial_validation(data, initial_errors):
	counter = 0
	initial_errors.clear()
	if not data['custom_fields']['HTTP-version']:
		initial_errors[counter] = "HTTP version not filled"
		counter += 1
		# print("key", app_name)
		# break
		

	if not data['custom_fields']['Personal'] and not data['custom_fields']['Corporate']:
		initial_errors[counter] = "Personal and Corporate both are empty, one of them should be filled"
		counter += 1

	if not data['custom_fields']['_Product_id']:
		initial_errors[counter] = "Product ID is missing"
		counter += 1

	return initial_errors



def login_and_login_fail_validation(data, activity_name, host_pattern, uri_pattern, login_loginFail_errors, activity_methods):
	activity_present = False
	counter = 0 
	login_loginFail_errors.clear()
	# print(activity_name)
		
	if (data['custom_fields'][activity_name+'_req-method'] != 'None') and (data['custom_fields'][activity_name+'_req-method'] != '')\
		 and (data['custom_fields'][activity_name+'_req-method'] != 'NA') and (data['custom_fields'][activity_name+'_req-method'] != 'REMAINING'):

		activity_present = True

		if data['custom_fields'][activity_name+'_req-method']:
			if not data['custom_fields'][activity_name+'_req-method'].lower() in activity_methods:
				login_loginFail_errors[counter] = " Request method value is incorrect"
				counter +=1

		if data['custom_fields'][activity_name+'_req-host']:
			
			if not host_pattern.search(data['custom_fields'][activity_name+'_req-host']):
				# print(data['custom_fields'][activity_name+'_req-host'])
				login_loginFail_errors[counter] = " Request host value seems to be incorrect"
				counter +=1
		else:
			login_loginFail_errors[counter] = " Host is missing"
			counter +=1

		if data['custom_fields'][activity_name+'_req-uri-path']:

			if not  uri_pattern.match(data['custom_fields'][activity_name+'_req-uri-path']):
				# print(data['custom_fields'][activity_name+'_req-uri-path'])
				login_loginFail_errors[counter] = " Request uri path value seems to be incorrect or starting '/' is missing(add /) or have space in starting(remove space)"
				counter +=1
		
		if data['custom_fields'][activity_name+'_req-headers']:
			if '|' in data['custom_fields'][activity_name+'_req-headers']:
				login_loginFail_errors[counter] = ' Error: Request header has pipe symbol, please replace it with comma'
				counter +=1


		if data['custom_fields'][activity_name+'_req-payload']:
			if '|' in data['custom_fields'][activity_name+'_req-payload']:
				login_loginFail_errors[counter] = ' Error: Request payload has pipe symbol, please replace it with comma'
				counter +=1

		if data['custom_fields'][activity_name+'_resp-header']:
			
			if '|' in data['custom_fields'][activity_name+'_resp-header']:
				# print(data['custom_fields'][activity_name+'_resp-header'])
				login_loginFail_errors[counter] = ' Error: Response header has pipe symbol, please replace it with comma'
				counter +=1

		if data['custom_fields'][activity_name+'_resp-payload']:
			if '|' in data['custom_fields'][activity_name+'_resp-payload']:
				login_loginFail_errors[counter] = ' Error: Response payload has pipe symbol, please replace it with comma'
				counter +=1

		if  uri_pattern.match(data['custom_fields'][activity_name+'_req-headers']):
			login_loginFail_errors[counter] = ' Request header value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if  uri_pattern.match(data['custom_fields'][activity_name+'_req-payload']):
			login_loginFail_errors[counter] = ' Request payload value seems to be incorrect (found same pattern as uri path)'
			counter +=1


		if  uri_pattern.match(data['custom_fields'][activity_name+'_resp-header']):
			login_loginFail_errors[counter] = ' Response header value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if  uri_pattern.match(data['custom_fields'][activity_name+'_resp-payload']):
			login_loginFail_errors[counter] = ' Response payload value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if  uri_pattern.match(data['custom_fields'][activity_name+'_resp-code']):
			login_loginFail_errors[counter] = ' response code value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if not data['custom_fields'][activity_name+'_resp-header'] and not data['custom_fields'][activity_name+'_resp-payload'] and not data['custom_fields'][activity_name+'_resp-code'] :
			# print(app_name)
			login_loginFail_errors[counter] =" Response not filled"
			counter +=1
			# print(login_loginFail_errors)

		if data['custom_fields'][activity_name+'_resp-code']:
			if not data['custom_fields'][activity_name+'_resp-code'].isdigit():
				# print(data['custom_fields'][activity_name+'_resp-code'])
				login_loginFail_errors[counter] =" Response code value is not integer"
				counter +=1

	if (data['custom_fields'][activity_name+'_req-method'] == 'None') or (data['custom_fields'][activity_name+'_req-method'] == ''):
		login_loginFail_errors[counter] = "Request method is empty, it should be filled"
		counter += 1

	if (data['custom_fields'][activity_name+'_req-method'] == 'NA') and (data['custom_fields'][activity_name+'_req-method'] == 'REMAINING'):
		if not data['custom_fields'][activity_name+'_req-host'] and not data['custom_fields'][activity_name+'_req-uri-path'] and \
			not data['custom_fields'][activity_name+'_req-params'] and not data['custom_fields'][activity_name+'_req-headers'] and \
			not data['custom_fields'][activity_name+'_req-payload'] and not data['custom_fields'][activity_name+'_resp-header'] and \
			not data['custom_fields'][activity_name+'_resp-payload']:
			pass
			# print(app_name)
			# print("all empty")
		else:
			login_loginFail_errors[counter] = "Request method is None/NA but all fields are not empty"
			counter += 1
			# print(login_loginFail_errors)
			# print("app name: ", app_name)
			# # break
			# pass
	
	return login_loginFail_errors, activity_present


def login_and_login_fail_depth(data, activity_name, params_depth_lst):
	params_depth_lst = []
	response = []

	if (data['custom_fields'][activity_name+'_req-method'] != 'None') and (data['custom_fields'][activity_name+'_req-method'] != '')\
		 and (data['custom_fields'][activity_name+'_req-method'] != 'NA') and (data['custom_fields'][activity_name+'_req-method'] != 'REMAINING'):

		if data['custom_fields'][activity_name+'_req-method']:
			params_depth_lst.append('_req-method')

		if data['custom_fields'][activity_name+'_req-host']:
			params_depth_lst.append('_req-host')
		
		if data['custom_fields'][activity_name+'_req-uri-path']:
			params_depth_lst.append('_req-uri-path')

		if data['custom_fields'][activity_name+'_req-params']:
			params_depth_lst.append('_req-params')

		if data['custom_fields'][activity_name+'_req-headers']:
			params_depth_lst.append('_req-headers')

		if data['custom_fields'][activity_name+'_req-payload']:
			params_depth_lst.append('_req-payload')

		if data['custom_fields'][activity_name+'_resp-code']:
			response.append('_resp-code')
			# params_depth_lst.append(activity_name+'_req-code')

		if data['custom_fields'][activity_name+'_resp-header']:
			response.append('_resp-header')

			# params_depth_lst.append(activity_name+'_req-header')

		if data['custom_fields'][activity_name+'_resp-payload']:
			response.append('_resp-payload')
			# params_depth_lst.append(activity_name+'_req-payload')
		
		if response:
			params_depth_lst.append(len(response))

	# print(params_depth_lst)
	return params_depth_lst


def logout_validation(data, activity_name, host_pattern, uri_pattern, logout_errors, activity_methods):
	counter = 0 
	activity_present = False

	if (data['custom_fields'][activity_name+'_req-method'] != 'None') and (data['custom_fields'][activity_name+'_req-method'] != '')\
		 and (data['custom_fields'][activity_name+'_req-method'] != 'NA') and (data['custom_fields'][activity_name+'_req-method'] != 'REMAINING'):

		activity_present = True
		if data['custom_fields'][activity_name+'_req-host']:
			if not host_pattern.search(data['custom_fields'][activity_name+'_req-host']):
				# print(data['custom_fields'][activity_name+'_req-host'])
				logout_errors[counter] = " Request host value seems to be incorrect"
				counter +=1
		else:
			logout_errors[counter] = " Host is missing"
			counter +=1

		if not data['custom_fields'][activity_name+'_req-method'].lower() in activity_methods:
			logout_errors[counter] = " Request method value is incorrect"
			counter +=1

		if data['custom_fields'][activity_name+'_req-uri-path']:

			if not uri_pattern.match(data['custom_fields'][activity_name+'_req-uri-path']):
				# print(data['custom_fields'][activity_name+'_req-uri-path'])
				logout_errors[counter] = " Request uri path value seems to be incorrect or starting '/' is missing(add /) or have space in starting(remove space)"
				counter +=1
		

		if data['custom_fields'][activity_name+'_response']:
			# print(app_name)
			logout_errors[counter] =" Response is filled, it should be empty"
			counter +=1
			# print(login_loginFail_errors)

		if  uri_pattern.match(data['custom_fields'][activity_name+'_req-headers']):
			logout_errors[counter] = ' Request header value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if  uri_pattern.match(data['custom_fields'][activity_name+'_req-payload']):
			logout_errors[counter] = ' Request header value seems to be incorrect (found same pattern as uri path)'
			counter +=1


	if (data['custom_fields'][activity_name+'_req-method'] == 'None') or (data['custom_fields'][activity_name+'_req-method'] == ''):
		logout_errors[counter] = "Request method is empty, it should be filled."
		counter += 1


	if (data['custom_fields'][activity_name+'_req-method'] == 'NA') or (data['custom_fields'][activity_name+'_req-method'] == 'REMAINING') :
		if not data['custom_fields'][activity_name+'_req-host'] and not data['custom_fields'][activity_name+'_req-uri-path'] and \
			not data['custom_fields'][activity_name+'_req-params'] and not data['custom_fields'][activity_name+'_req-headers'] and \
			not data['custom_fields'][activity_name+'_req-payload'] and not data['custom_fields'][activity_name+'_response']:
			pass
			# print(app_name)
			# print("all empty")
		else:
			logout_errors[counter] = "Request method is None but all fields are not empty"
			counter += 1

	
	return logout_errors, activity_present


def other_Acitivies_validation(data, activity_name, host_pattern, uri_pattern, other_activities_errors, activity_methods):
	counter = 0 
	activity_present = False
	other_activities_errors.clear()
	# print(data['custom_fields'][activity_name+'_req-method'])
	if (data['custom_fields'][activity_name+'_req-method'] != 'None') and (data['custom_fields'][activity_name+'_req-method'] != '')  \
		and (data['custom_fields'][activity_name+'_req-method'] != 'NA') and (data['custom_fields'][activity_name+'_req-method'] != 'REMAINING'):

		activity_present = True

		if not data['custom_fields'][activity_name+'_req-method'].lower() in activity_methods:
			other_activities_errors[counter] = " Request method value is incorrect"
			counter +=1


		if data['custom_fields'][activity_name+'_req-host']:

			if not host_pattern.search(data['custom_fields'][activity_name+'_req-host']):
				# print(":::::::::::::::::::::::")
				# print(host_pattern.search(data['custom_fields'][activity_name+'_req-host']))
				# print(data['custom_fields'][activity_name+'_req-host'])
				other_activities_errors[counter] = " Request host value seems to be incorrect"
				counter +=1

		else:
			other_activities_errors[counter] = " Host is missing"
			counter +=1

		if uri_pattern.match(data['custom_fields'][activity_name+'_req-params']):
			other_activities_errors[counter] = ' Params value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if  uri_pattern.match(data['custom_fields'][activity_name+'_req-headers']):
			other_activities_errors[counter] = ' Request header value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if uri_pattern.match(data['custom_fields'][activity_name+'_req-payload']):
			# print(data['custom_fields'][activity_name+'_req-payload'])
			other_activities_errors[counter] = ' Request payload value seems to be incorrect (found same pattern as uri path)'
			counter +=1

		if data['custom_fields'][activity_name+'_req-uri-path']:

			if not uri_pattern.match(data['custom_fields'][activity_name+'_req-uri-path']):
				# print(data['custom_fields'][activity_name+'_req-uri-path'])
				other_activities_errors[counter] = " Request uri path value seems to be incorrect or starting '/' is missing(add /) or have space in starting(remove space)"
				counter +=1
		

		if data['custom_fields'][activity_name+'_response']:
			# print(app_name)
			other_activities_errors[counter] =" Response is filled, it should be empty"
			counter +=1
			# print(login_loginFail_errors)

	
	if (data['custom_fields'][activity_name+'_req-method'] == 'None') or (data['custom_fields'][activity_name+'_req-method'] == ''):
		other_activities_errors[counter] = "Request method is empty, it should be filled."
		counter += 1

	if (data['custom_fields'][activity_name+'_req-method'] == 'NA') or (data['custom_fields'][activity_name+'_req-method'] == 'REMAINING'):
		if not data['custom_fields'][activity_name+'_req-host'] and not data['custom_fields'][activity_name+'_req-uri-path'] and \
			not data['custom_fields'][activity_name+'_req-params'] and not data['custom_fields'][activity_name+'_req-headers'] and \
			not data['custom_fields'][activity_name+'_req-payload'] and not data['custom_fields'][activity_name+'_response']:
			pass
			# print(app_name)
			# print("all empty")
		else:
			other_activities_errors[counter] = "Request method is None but all fields are not empty"
			counter += 1
			# print(login_loginFail_errors)
			# print("app name: ", app_name)
			# break
			pass

	
	return other_activities_errors, activity_present


def multiple_methods_validation(data, activity_name, multiple_methods_error , multiple_methods_err_lst, activity_methods):
	error_check = False 
	methods_ls = []
	if data['custom_fields'][activity_name+'_req-method'] != 'None' and data['custom_fields'][activity_name+'_req-method'] != '' and data['custom_fields'][activity_name+'_req-method'] != 'NA' and data['custom_fields'][activity_name+'_req-method'] != 'REMAINING':
		
		# if not ['custom_fields'][activity_name+'_req-method'] in activity_methods:
		# 	print("Req")

		methods_ls.append(data['custom_fields'][activity_name+'_req-method'])







		if data['custom_fields'][activity_name+'_req-method-2'] or ("|" in data['custom_fields'][activity_name+'_req-host']) or ("|" in data['custom_fields'][activity_name+'_req-uri-path']) or ("|" in data['custom_fields'][activity_name+'_req-params']) or ("|" in data['custom_fields'][activity_name+'_req-headers']) or ("|" in data['custom_fields'][activity_name+'_req-payload']):

			counter = 0
			value = data['custom_fields'][activity_name+'_req-method-2']
			methods_splitter = value.split('|')
			for methods in methods_splitter:
				methods_ls.append(methods)
			
			methods_ls_len = len(methods_ls)

			for method in methods_ls:
				if not method.lower() in activity_methods:
					multiple_methods_err_lst = " One or more request method values are incorrect "
					counter += 1
				
			if data['custom_fields'][activity_name+'_req-host']:
				value = data['custom_fields'][activity_name+'_req-host']
				hosts_splitter = value.split('|')

				if not (methods_ls_len == len(hosts_splitter)):
					error_check = True				

			if data['custom_fields'][activity_name+'_req-uri-path']:
				value = data['custom_fields'][activity_name+'_req-uri-path']
				uri_splitter = value.split('|')

				if not (methods_ls_len == len(uri_splitter)):
					error_check = True

			if data['custom_fields'][activity_name+'_req-params']:
				value = data['custom_fields'][activity_name+'_req-params']
				params_splitter = value.split('|')

				if not (methods_ls_len == len(params_splitter)):
					error_check = True

			if data['custom_fields'][activity_name+'_req-headers']:
				value = data['custom_fields'][activity_name+'_req-headers']
				req_header_splitter = value.split('|')

				if not (methods_ls_len == len(req_header_splitter)):
					error_check = True

			if data['custom_fields'][activity_name+'_req-payload']:
				value = data['custom_fields'][activity_name+'_req-payload']
				req_payload_splitter = value.split('|')

				if not (methods_ls_len == len(req_payload_splitter)):
					error_check = True


			if data['custom_fields'][activity_name+'_response']:
				value = data['custom_fields'][activity_name+'_response']
				response_splitter = value.split('|')

				if not (methods_ls_len == len(response_splitter)):
					error_check = True


	if error_check:
		multiple_methods_error = "Incorrect information against multiple methods"
	else: 
		multiple_methods_error = ""

	return multiple_methods_error, multiple_methods_err_lst

def multiple_values_validation(data, activity_name, multiple_values_error ):
	check = False
	multiple_values_error = ''
	values_length = []
	methods_ls = []
	max_len = 0

	if data['custom_fields'][activity_name+'_req-method'] != 'None' and data['custom_fields'][activity_name+'_req-method'] != '' and data['custom_fields'][activity_name+'_req-method'] != 'NA' and data['custom_fields'][activity_name+'_req-method'] != 'REMAINING' :
		
		
		methods_ls.append(data['custom_fields'][activity_name+'_req-method'])

		if data['custom_fields'][activity_name+'_req-method-2']:
			value = data['custom_fields'][activity_name+'_req-method-2']
			methods_splitter = value.split('|')
			for methods in methods_splitter:
				methods_ls.append(methods)
			
			# methods_ls_len = len(methods_ls)
			values_length.append( len(methods_ls))
			
		if data['custom_fields'][activity_name+'_req-host']:
			value = data['custom_fields'][activity_name+'_req-host']
		
			hosts_splitter = value.split('|')
			values_length.append(len(hosts_splitter))
			#hosts_ls.append(hosts_splitter)

			# if not (methods_ls_len == len(hosts_splitter)):
			# 	error_check = True				

		if data['custom_fields'][activity_name+'_req-uri-path']:
			value = data['custom_fields'][activity_name+'_req-uri-path']
			uri_splitter = value.split('|')
			#uri_ls.append(uri_splitter)
			values_length.append(len(uri_splitter))


			# if not (methods_ls_len == len(uri_splitter)):
			# 	error_check = True

		if data['custom_fields'][activity_name+'_req-params']:
			value = data['custom_fields'][activity_name+'_req-params']
			params_splitter = value.split('|')
			values_length.append(len(params_splitter))
			#params_ls.append(params_splitter)

			# if not (methods_ls_len == len(params_splitter)):
			# 	error_check = True

		if data['custom_fields'][activity_name+'_req-headers']:
			value = data['custom_fields'][activity_name+'_req-headers']
			req_header_splitter = value.split('|')
			values_length.append(len(req_header_splitter))
			# req_head_ls.append(req_header_splitter)

			# if not (methods_ls_len == len(req_header_splitter)):
			# 	error_check = True

		if data['custom_fields'][activity_name+'_req-payload']:
			value = data['custom_fields'][activity_name+'_req-payload']
			req_payload_splitter = value.split('|')
			values_length.append(len(req_payload_splitter))
			# req_payload_ls.append(req_payload_splitter)
			# if not (methods_ls_len == len(req_payload_splitter)):
			# 	error_check = True


		if data['custom_fields'][activity_name+'_response']:
			value = data['custom_fields'][activity_name+'_response']
			response_splitter = value.split('|')
			values_length.append(len(response_splitter))
			#response_ls.append(len(response_splitter))
			# if not (methods_ls_len == len(response_splitter)):
			# 	error_check = True
	

		if len(set(values_length)) != 1:
			check = True
			
		else: 
			check = False
		
		if len(values_length) > 1:
			max_len = max(values_length)
		elif len(values_length) == 1:
			max_len = 1
		else:
			max_len = 0

			
	if check:
		multiple_values_error = "Error: HTTP sessions depth not same"
	else: 
		multiple_values_error = ""

	return multiple_values_error, max_len


	# # if methods_ls
	
	# if error_check:
	# 	multiple_values_error = "Error: HTTP sessions depth not same"
	# else: 
	# 	multiple_values_error = ""

	# return multiple_values_error



def attachment_names_validation(attachments_names, activity_name, app_ticket, activity_count):
	lst = []
	validate_pcap = ''
	if activity_count == 0:
		validate_pcap = str(app_ticket)+"_"+activity_name+"-"+str(activity_count)
		if (validate_pcap+".pcap" in attachments_names) or (validate_pcap+".PCAP" in attachments_names):
			pass
			# lst.append("Correct fileName")
		else:
			print(validate_pcap)
			print(attachments_names)
			lst.append("Incorrect fileName")
	elif activity_count > 0:
		for i in range(activity_count):
			validate_pcap = str(app_ticket)+"_"+activity_name+"-"+str(i)
			# print(validate_pcap)
			if (validate_pcap+".pcap" in attachments_names) or (validate_pcap+".PCAP" in attachments_names):
				# lst.append("Correct fileName")
				pass
			else:
				lst.append("Incorrect fileName")
	
	return lst


# for assembla wrapper
assembla = API(
    key=access_key,
    secret=access_secret,
    # Auth details from https://www.assembla.com/user/edit/manage_clients
)

# for assembla api
my_headers = {'X-Api-Key' : access_key,
            'X-Api-Secret': access_secret,
            }


activity_methods = ['delete', 'get', 'patch', 'post', 'put', 'remaining', 'na']

my_space= ''
while my_space == '':
	try:
		# To get data from assembla
		space_name='Granular Controls'
		my_space= assembla.spaces(name=space_name)[0]
		#print(len(my_space.tickets()))
		#below method call to hit the assembla api
		assembla_data_to_json( my_space, my_headers, drop2_tickets,drop3_tickets, drop4_tickets)
		break
	except:
		print("Connection refused by the server..")
		time.sleep(5)
		print("Was a nice sleep, now let me continue...")
		continue


with open('assembla_data') as f:
  data = json.load(f)


re_pattern_for_host = "(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
host_pattern = re.compile(re_pattern_for_host)

re_pattern_for_uri =r"(^\/.*)"
uri_pattern = re.compile(re_pattern_for_uri)
user = {}


for app_name, value in data.items():


	error_logs = {}
	errors_dict = {}
	initial_errors = {}
	login_loginFail_errors = {}
	login_errors = {}
	login_file_error = {}

	loginFail_errors={}
	loginFail_file_error = {}

	logout_errors = {}
	logout_file_error = {}


	upload_errors = {}
	upload_multiple_methods_err = {}
	upload_multiple_methods_err_lst = {}
	upload_multiple_values_err = {}
	upload_file_error = {}

	download_errors = {}
	download_multiple_methods_err = {}
	download_multiple_methods_err_lst = {}
	download_multiple_values_err = {}
	download_file_error = {}

	delete_errors = {}
	delete_multiple_methods_err = {}
	delete_multiple_methods_err_lst = {}
	delete_multiple_values_err = {}
	delete_file_error = {}

	share_errors = {}
	share_multiple_methods_err = {}
	share_multiple_methods_err_lst = {}
	share_multiple_values_err = {}
	share_file_error = {}

	readonly_errors = {}
	readonly_multiple_methods_err = {}
	readonly_multiple_methods_err_lst = {}
	readonly_multiple_values_err = {}
	readonly_file_error = {}

	upload_values_count = 0
	download_values_count = 0
	delete_values_count = 0
	share_values_count = 0
	readonly_values_count = 0

	
	attachement_status = ""
	

	login_depth_lst = []
	loginFail_depth_lst = []

	activity_flag = False
	activies_present = []

	#if app_name == 'Sitefinity Digital Experience Cloud':
	if value['Status'] == 'Pcap Checks' or value['Status'] == 'Pcap Done' or value['Status'] == 'XML Done':
		initial_errors = initial_validation(value, initial_errors)

		activity_name = 'LOGIN'
		login_errors, activity_flag = login_and_login_fail_validation(value, activity_name, host_pattern, uri_pattern,login_errors, activity_methods)
		activies_present.append(activity_flag)
		login_depth_lst = login_and_login_fail_depth(value, activity_name, login_depth_lst)
		login_acitivty_count = 1
		if activity_flag:
			login_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], login_acitivty_count-1)
		# print("Login depth")
		# print(login_depth_lst )

		activity_name = 'LOGIN-FAIL'
		loginFail_errors, activity_flag = login_and_login_fail_validation(value, activity_name, host_pattern, uri_pattern, loginFail_errors, activity_methods)
		activies_present.append(activity_flag)
		loginFail_depth_lst = login_and_login_fail_depth(value, activity_name, loginFail_depth_lst)
		loginFail_acitivty_count = 1
		if activity_flag:
			loginFail_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], loginFail_acitivty_count-1)
		# print("Login-fail depth")
		# print(loginFail_depth_lst)
		# print((login_depth_lst))
		# print((loginFail_depth_lst))
		# if login_depth_lst == loginFail_depth_lst:
		# 	print('yesss')

		if login_depth_lst or loginFail_depth_lst:
			for x, y in zip(login_depth_lst, loginFail_depth_lst):
				if x != y:
					depth = "Failed: Incorrect depth between login and login-fail"
				else:
					depth = ""
		# print(depth)
		# if not (set(login_depth_lst) == set(loginFail_depth_lst)):
		# 	depth = "Failed: Incorrect depth between login and login-fail"
		# else:
		# 	depth = ""
		# print(depth)
		activity_name = 'LOGOUT'
		logout_errors, activity_flag = logout_validation(value, activity_name, host_pattern, uri_pattern, logout_errors, activity_methods)
		activies_present.append(activity_flag)
		logout_acitivty_count = 1
		if activity_flag:
			logout_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], logout_acitivty_count-1)
		# print(logout_errors)


		activity_name = 'UPLOAD'
		upload_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, upload_errors, activity_methods)
		activies_present.append(activity_flag)
		upload_multiple_methods_err, upload_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, upload_multiple_methods_err,upload_multiple_methods_err_lst, activity_methods)
		upload_multiple_values_err, upload_values_count = multiple_values_validation(value, activity_name, upload_multiple_values_err)
		if activity_flag:
			upload_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], upload_values_count-1)



		activity_name = 'DOWNLOAD'
		download_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, download_errors, activity_methods)
		activies_present.append(activity_flag)
		download_multiple_methods_err, download_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, download_multiple_methods_err, download_multiple_methods_err_lst, activity_methods)
		download_multiple_values_err, download_values_count = multiple_values_validation(value, activity_name, download_multiple_values_err)
		if activity_flag:
			download_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], download_values_count-1)

		# print(download_multiple_methods_err)


		activity_name = 'DELETE'
		delete_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, delete_errors, activity_methods)
		activies_present.append(activity_flag)
		delete_multiple_methods_err, delete_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, delete_multiple_methods_err,  delete_multiple_methods_err_lst, activity_methods)
		delete_multiple_values_err, delete_values_count = multiple_values_validation(value, activity_name, delete_multiple_values_err)
		if activity_flag:
			delete_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], delete_values_count-1)


		# print(delete_multiple_methods_err)

		
		activity_name = 'SHARE'
		share_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, share_errors, activity_methods)
		activies_present.append(activity_flag)
		share_multiple_methods_err, share_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, share_multiple_methods_err,  share_multiple_methods_err_lst, activity_methods)
		share_multiple_values_err, share_values_count = multiple_values_validation(value, activity_name, share_multiple_values_err)
		if activity_flag:
			share_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], share_values_count-1)

		# print(share_multiple_methods_err)

		activity_name = 'READ-ONLY'
		readonly_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, readonly_errors, activity_methods)
		activies_present.append(activity_flag)
		readonly_multiple_methods_err, readonly_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, readonly_multiple_methods_err, readonly_multiple_methods_err_lst, activity_methods)
		readonly_multiple_values_err, readonly_values_count = multiple_values_validation(value, activity_name, readonly_multiple_values_err)
		if activity_flag:
			readonly_file_error = attachment_names_validation(value['Attachments_list'], activity_name, value['Ticket_number'], readonly_values_count-1)
		# print(readonly_multiple_methods_err)


		if len(initial_errors) > 0:
			errors_dict['Initial'] = initial_errors

		if len(login_errors) > 0:
			errors_dict['LOGIN'] = login_errors

		if len(login_file_error) > 0:
			errors_dict['LOGIN-Filename-Error'] = login_file_error


		if len(loginFail_errors) > 0:
			errors_dict['LOGIN-FAIL'] = loginFail_errors

		if len(loginFail_file_error) > 0:
			errors_dict['LOGIN-FAIL-Filename-Error'] = loginFail_file_error

		if depth:
			errors_dict['LOGIN_LOGIN-FAIL_DEPTH'] = depth

		if len(logout_errors) > 0:
			errors_dict['LOGOUT'] =logout_errors

		if len(logout_file_error) > 0:
			errors_dict['LOGOUT-Filename-Error'] = logout_file_error



		if len(upload_errors) > 0:
			errors_dict['UPLOAD'] =upload_errors

		if upload_multiple_methods_err:
			errors_dict['UPLOAD-MULTIPLE-METHODS'] =upload_multiple_methods_err

		if upload_multiple_methods_err_lst:
			errors_dict['UPLOAD-MULTIPLE-METHODS-VALIDATION'] =upload_multiple_methods_err_lst

		if upload_multiple_values_err:
			errors_dict['UPLOAD-MULTIPLE-VALUES'] =upload_multiple_values_err

		if len(upload_file_error) > 0:
			errors_dict['UPLOAD-Filename-Error'] = upload_file_error

		if len(download_errors) > 0:
			errors_dict['DOWNLOAD'] =download_errors

		if download_multiple_methods_err:
			errors_dict['DOWNLOAD-MULTIPLE-METHODS'] =download_multiple_methods_err

		if download_multiple_methods_err_lst:
			errors_dict['DOWNLOAD-MULTIPLE-METHODS-VALIDATION'] =download_multiple_methods_err_lst

		if download_multiple_values_err:
			errors_dict['DOWNLOAD-MULTIPLE-VALUES'] =download_multiple_values_err

		if len(download_file_error) > 0:
			errors_dict['DOWNLOAD-Filename-Error'] = download_file_error

		if len(delete_errors) > 0:
			errors_dict['DELETE'] =delete_errors

		if delete_multiple_methods_err:
			errors_dict['DELETE-MULTIPLE-METHODS'] =delete_multiple_methods_err

		if delete_multiple_methods_err_lst:
			errors_dict['DELETE-MULTIPLE-METHODS-VALIDATION'] =delete_multiple_methods_err_lst

		if delete_multiple_values_err:
			errors_dict['DELETE-MULTIPLE-VALUES'] =delete_multiple_values_err

		if len(delete_file_error)>0:
			errors_dict['DELETE-Filename-Error'] = download_file_error

		if len(share_errors) > 0:
			errors_dict['SHARE'] =share_errors

		if share_multiple_methods_err:
			errors_dict['SHARE-MULTIPLE-METHODS'] =share_multiple_methods_err

		if share_multiple_methods_err_lst:
			errors_dict['SHARE-MULTIPLE-METHODS-VALIDATION'] =share_multiple_methods_err_lst

		if share_multiple_values_err:
			errors_dict['SHARE-MULTIPLE-VALUES'] =share_multiple_values_err
		
		if len(share_file_error) > 0:
			errors_dict['SHARE-Filename-Error'] = share_file_error

		if len(readonly_errors) > 0:
			errors_dict['READ-ONLY'] =readonly_errors

		if readonly_multiple_methods_err:
			errors_dict['READ-ONLY-MULTIPLE-METHODS'] =readonly_multiple_methods_err

		if readonly_multiple_methods_err_lst:
			errors_dict['READONLY-MULTIPLE-METHODS-VALIDATION'] =readonly_multiple_methods_err_lst

		if readonly_multiple_values_err:
			errors_dict['READ-ONLY-MULTIPLE-VALUES'] =readonly_multiple_values_err

		if len(readonly_file_error) > 0 :
			errors_dict['READ-ONLY-Filename-Error'] = readonly_file_error

		if upload_values_count != 0:
			upload_count = upload_values_count - 1
		else:
			upload_count = upload_values_count

		if download_values_count != 0:
			download_count = download_values_count - 1
		else:
			download_count = download_values_count

		if delete_values_count != 0:
			delete_count = delete_values_count - 1
		else:
			delete_count = delete_values_count

		if share_values_count != 0:
			share_count = share_values_count - 1
		else:
			share_count = share_values_count

		if readonly_values_count != 0:
			readonly_count = readonly_values_count - 1
		else:
			readonly_count = readonly_values_count

		# checking if the attachment count is equal to the activities done
		overall_activities_count  = sum(activies_present) + upload_count + download_count + delete_count + share_count + readonly_count
		# print(app_name)
		# print(overall_activities_count)
		# print(value["Attachments_count"])
		# print(app_name)
		if overall_activities_count  == value["Attachments_count"]:
			attachement_status = ""
		else:
			attachement_status = "Failed: Incorrect number of attachments present against performed activities"
		
		if attachement_status:
			errors_dict['Attachements Status'] = attachement_status

		if len(errors_dict) > 0:
			# print(errors_dict)
			error_logs[app_name+" "+value['custom_fields']["_Product_id"]] = errors_dict

		key = value['Assigned to']
	
		if key not in user.keys():
			if error_logs:
				user[key] = error_logs	
		else:
			if error_logs:
				user[key].update(error_logs)

		print("Validating data... Please wait!!")


# # print(len(user))
# print(user)
for key, value in user.items():
	# print(key)
	# print(len(value))
	
	with open(key+'.json', 'w') as outfile:
		json.dump(value, outfile,indent=4)
	# pprint( list(user.keys()) )

# print(len(user))
