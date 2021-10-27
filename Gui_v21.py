from tkinter import *
from tkinter import messagebox
#Requirement:
#make a creds_personal file for ticket access having access_key & access_secret
import json
from creds_personal import access_key, access_secret
from assembla import API,Ticket
import requests
from pprint import pprint
import re
import time



def assembla_data_to_json(input_gc, my_space, my_headers):
	count = 0
	ticket_ls = []
	assembla_data = {}
	
	print("\nPlease wait....")
	print("Working for GC-",input_gc)
	for ticket in my_space.tickets():
		# print(ticket)
		attachment_list_json = []
		attachments_temp = []
		attachement_names = []
		# print(ticket['number'])
		for gc in input_gc:
			# print(gc)
			if int(ticket['number']) == int(gc) :
				count += 1
				ticket_number = ticket['number']
				ticket_ls.append(ticket_number)
				# print("Fetching Assembla data.. Please wait...")
				space_name = "Granular-Controls"
				api = f'https://api.assembla.com/v1/spaces/{space_name}/tickets/{ticket_number}/attachments.json'
				attachment_api_get = api
				api_response = requests.get(attachment_api_get, headers=my_headers)
				response = api_response.text
				
				if len(response) > 0: 
					attachment_list_json = json.loads(api_response.text)
					for attachment in attachment_list_json:
						name = attachment['name'].split('.')
						if name[-1] == 'saz' or name[-1] == 'SAZ':
							attachments_temp.append(attachment_list_json)
							attachement_names.append(attachment['name'])

					
			
		            # get assembla data through assembla wrapper
					assembla_data[str(ticket_number)] = { 'Summary': ticket['summary'], 'Ticket_number': str(ticket_number), 'Status': ticket['status'] ,'custom_fields': ticket['custom_fields'], 'Attachments_count': len(attachments_temp), 'Attachments_list':	attachement_names }
					# print(assembla_data)
		# with open('assembla_data', 'w') as fp:  
		# 	json.dump(assembla_data,fp,indent=1)
	return assembla_data


def initial_validation(data, initial_errors):
	counter = 0
	initial_errors.clear()
	if not data['custom_fields']['HTTP-version']:
		initial_errors[counter] = "HTTP version not filled"
		counter += 1
		# print("key", app_name)
		# break
		
	if (data['custom_fields']['Personal Placeholder'] == '' or data['custom_fields']['Personal Placeholder'] == None) and (data['custom_fields']['Corporate Placeholder'] == '' or data['custom_fields']['Corporate Placeholder'] == None):
	#if not data['custom_fields']['Personal'] and not data['custom_fields']['Corporate']:
		initial_errors[counter] = "Personal and Corporate Placeholders both are empty, one of them should be filled"
		counter += 1
	
	if (data['custom_fields']['Personal Placeholder'] != '' or data['custom_fields']['Personal Placeholder'] == None):
		if data['custom_fields']['Personal Placeholder'] != 'NA':
			if str(data['custom_fields']['Personal Info']).strip() == '' and str(data['custom_fields']['Personal Info']).strip() == None and str(data['custom_fields']['Personal Info']).strip().lower() == "na":
				initial_errors[counter] = "Personal Info is not correctly filled"
				counter += 1	

	if (data['custom_fields']['Corporate Placeholder'] != '' or data['custom_fields']['Corporate Placeholder'] == None):
		if data['custom_fields']['Corporate Placeholder'] != 'NA':
			if str(data['custom_fields']['Corporate Info']).strip() == '' and str(data['custom_fields']['Corporate Info']).strip() == None and str(data['custom_fields']['Corporate Info']).strip().lower() == "na":
				initial_errors[counter] = "Corporate Info is not correctly filled"
				counter += 1	
	
	if str(data['custom_fields']['username']).strip() == '' or str(data['custom_fields']['password']).strip() == '':
		initial_errors[counter] = "Username or password cannot be empty."
		counter += 1

	if str(data['custom_fields']['_Priority']).strip() == '':
		initial_errors[counter] = "Priority is Empty, Incorrect Apps done!! please discuss with team."
	
	if str(data['custom_fields']['Web URL']).strip() == '' :
		initial_errors[counter] = "Web URL cannot be empty."
		counter += 1
	else:
		if '|' in str(data['custom_fields']['Web URL']).strip():
			pipe_split = str(data['custom_fields']['Web URL']).lower().strip().split("|")
			for pipe in pipe_split:
				if str(pipe).strip().lower().startswith("https://") or str(pipe).lower().strip().startswith("http://") or str(pipe).lower().strip().startswith("www") or str(pipe).lower().strip().endswith("/"):
					initial_errors[counter] = "Web URL pattern is incorrect, please correct it."
					counter += 1
					break
		else:
			if str(data['custom_fields']['Web URL']).lower().strip().startswith("https://") or str(data['custom_fields']['Web URL']).lower().strip().startswith("http://") or str(data['custom_fields']['Web URL']).lower().strip().startswith("www") or str(data['custom_fields']['Web URL']).lower().strip().endswith("/"):
				initial_errors[counter] = "Web URL pattern is incorrect, please correct it."
				counter += 1

				
	if not data['custom_fields']['_Product_id']:
		initial_errors[counter] = "Product ID is missing"
		counter += 1

	return initial_errors

def asterik_check(search_string, original_string):

	res = [i.start() for i in re.finditer(search_string, original_string)] 
	last_char = len(original_string) - 1

	
	if 0 in res:
		index = res.index(0)
		res.pop(index)



	if last_char in res:
		index = res.index(last_char)
		res.pop(index)

	
	if len(res) > 0:
		return True
	else:
		return False


def login_and_login_fail_validation(data, activity_name, host_pattern, uri_pattern, login_loginFail_errors, activity_methods, blacklist_words):
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
			
			if str(data['custom_fields'][activity_name+'_req-host']).startswith(" "):
				login_loginFail_errors[counter] = " Request host starts with whitespace, please remove it."
				counter +=1

			if any(x in str(data['custom_fields'][activity_name+'_req-host']).lower() for x in blacklist_words):
				login_loginFail_errors[counter] = " Error: Some of the blacklisted words are present in Request host"
				counter +=1

			check_host = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-host']))
			if check_host == True :
				login_loginFail_errors[counter] = " Error: Asterik cannot be present in between request host value, please fix it"
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-host']).startswith("."):
				login_loginFail_errors[counter] = " Error: Host value cannot startswith dot, please fix it"
				counter +=1

		else:
			login_loginFail_errors[counter] = " Host is missing"
			counter +=1

		if data['custom_fields'][activity_name+'_req-uri-path']:

			if not  uri_pattern.match(data['custom_fields'][activity_name+'_req-uri-path']):
				# print(data['custom_fields'][activity_name+'_req-uri-path'])
				login_loginFail_errors[counter] = " Request uri path value seems to be incorrect or starting '/' is missing(add /) or have space in starting(remove space)"
				counter +=1
			
			if str(data['custom_fields'][activity_name+'_req-uri-path']).startswith(" "):
				login_loginFail_errors[counter] = " Request uri starts with whitespace, please remove it."
				counter +=1


			if any(x in str(data['custom_fields'][activity_name+'_req-uri-path']).lower() for x in blacklist_words):
				login_loginFail_errors[counter] = " Error: Some of the blacklisted words are present in Request uri"
				counter +=1


		if data['custom_fields'][activity_name+'_req-params']:
			if '|' in data['custom_fields'][activity_name+'_req-params']:
				login_loginFail_errors[counter] = ' Error: Request params has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-params']).startswith(" "):
				login_loginFail_errors[counter] = " Request params starts with whitespace, please remove it."
				counter +=1

			if any(x in str(data['custom_fields'][activity_name+'_req-params']).lower() for x in blacklist_words):
				login_loginFail_errors[counter] = " Error: Some of the blacklisted words are present in Request params"
				counter +=1

			if ',' in data['custom_fields'][activity_name+'_req-params']:
				req_params_comma_splitter = data['custom_fields'][activity_name+'_req-params'].split(",")
				for req_params_comma_split in req_params_comma_splitter:
					check_params  = asterik_check(r"\*",str(req_params_comma_split))
					if check_params == True:
						login_loginFail_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
						counter +=1

			else:
				check_params  = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-params']))
				if check_params == True:
					login_loginFail_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
					counter +=1

		if data['custom_fields'][activity_name+'_req-headers']:
			if '|' in data['custom_fields'][activity_name+'_req-headers']:
				login_loginFail_errors[counter] = ' Error: Request header has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-headers']).startswith(" "):
				login_loginFail_errors[counter] = " Request header starts with whitespace, please remove it."
				counter +=1
	
			if any(x in str(data['custom_fields'][activity_name+'_req-headers']).lower() for x in blacklist_words):
				login_loginFail_errors[counter] = " Error: Some of the blacklisted words are present in Request header"
				counter +=1

			if "," in data['custom_fields'][activity_name+'_req-headers']:
				req_head_comma_splitter = data['custom_fields'][activity_name+'_req-headers'].split(",")

				for req_head_comma_split in req_head_comma_splitter:
					check_req_head  = asterik_check(r"\*",str(req_head_comma_split))
					if check_req_head == True:
						login_loginFail_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
						counter +=1

			else:
				check_req_head  = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-headers']))
				if check_req_head == True:
					login_loginFail_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
					counter +=1


		if data['custom_fields'][activity_name+'_req-payload']:
			if '|' in data['custom_fields'][activity_name+'_req-payload']:
				login_loginFail_errors[counter] = ' Error: Request payload has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-payload']).startswith(" "):
				login_loginFail_errors[counter] = " Request payload starts with whitespace, please remove it."
				counter +=1

			if any(x in str(data['custom_fields'][activity_name+'_req-payload']).lower() for x in blacklist_words):
				login_loginFail_errors[counter] = " Error: Some of the blacklisted words are present in Request payload"
				counter +=1

			if ',' in data['custom_fields'][activity_name+'_req-payload']:
				req_pay_comma_splitter = data['custom_fields'][activity_name+'_req-payload'].split(",")
				for req_pay_comma_split in req_pay_comma_splitter:
					check_req_pay = asterik_check(r"\*",str(req_pay_comma_split))
					if check_req_pay == True:
						login_loginFail_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
						counter +=1

			else:
				check_req_pay = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-payload']))
				if check_req_pay == True:
					login_loginFail_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
					counter +=1

		if data['custom_fields'][activity_name+'_resp-header']:
			
			if '|' in data['custom_fields'][activity_name+'_resp-header']:
				# print(data['custom_fields'][activity_name+'_resp-header'])
				login_loginFail_errors[counter] = ' Error: Response header has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_resp-header']).startswith(" "):
				login_loginFail_errors[counter] = " Response header starts with whitespace, please remove it."
				counter +=1

			if any(x in str(data['custom_fields'][activity_name+'_resp-header']).lower() for x in blacklist_words):
				login_loginFail_errors[counter] = " Error: Some of the blacklisted words are present in Response header"
				counter +=1

			if ',' in data['custom_fields'][activity_name+'_resp-header']:
				resp_header_comma_splitter = data['custom_fields'][activity_name+'_resp-header'].split(",")
				for resp_header_comma_split in resp_header_comma_splitter:
					check_res_head = asterik_check(r"\*",str(resp_header_comma_split))
					if check_res_head == True:
						login_loginFail_errors[counter] = " Error: Asterik cannot be present in between response head value, please fix it"
						counter +=1

			else:
				check_res_head = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_resp-header']))
				if check_res_head == True:
					login_loginFail_errors[counter] = " Error: Asterik cannot be present in between response head value, please fix it"
					counter +=1



		if data['custom_fields'][activity_name+'_resp-payload']:
			if '|' in data['custom_fields'][activity_name+'_resp-payload']:
				login_loginFail_errors[counter] = ' Error: Response payload has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_resp-payload']).startswith(" "):
				login_loginFail_errors[counter] = " Response payload starts with whitespace, please remove it."
				counter +=1

			if any(x in str(data['custom_fields'][activity_name+'_resp-payload']).lower() for x in blacklist_words):
				login_loginFail_errors[counter] = " Error: Some of the blacklisted words are present in Response payload"
				counter +=1

			if ',' in data['custom_fields'][activity_name+'_resp-payload']:
				resp_payload_comma_splitter = data['custom_fields'][activity_name+'_resp-payload'].split(",")
				for resp_payload_comma_split in resp_payload_comma_splitter:
					check_res_pay = asterik_check(r"\*",str(resp_payload_comma_split))
					if check_res_pay == True:
						login_loginFail_errors[counter] = " Error: Asterik cannot be present in between response payload value, please fix it"
						counter +=1

			else:
				check_res_pay = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_resp-payload']))
				if check_res_pay == True:
					login_loginFail_errors[counter] = " Error: Asterik cannot be present in between response payload value, please fix it"
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



def logout_validation(data, activity_name, host_pattern, uri_pattern, logout_errors, activity_methods, blacklist_words):
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

			if '|' in data['custom_fields'][activity_name+'_req-host']:
				# print(data['custom_fields'][activity_name+'_resp-header'])
				logout_errors[counter] =  ' Error: Request host has pipe symbol, please replace it with comma'
				counter +=1

			if any(x in str(data['custom_fields'][activity_name+'_req-host']).lower() for x in blacklist_words):
				logout_errors[counter] = " Error: Some of the blacklisted words are presentin Request host"
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-host']).startswith(" "):
				logout_errors[counter] =  " Request host starts with whitespace, please remove it."
				counter +=1

			check_host = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-host']))
			if check_host == True :
				logout_errors[counter] = " Error: Asterik cannot be present in between request host value, please fix it"
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-host']).startswith("."):
				logout_errors[counter] = " Error: Asterik cannot be present in between request host value, please fix it"
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

			if any(x in str(data['custom_fields'][activity_name+'_req-uri-path']).lower() for x in blacklist_words):
				logout_errors[counter] = " Error: Some of the blacklisted words are present in Request uri"
				counter +=1
			
			if '|' in data['custom_fields'][activity_name+'_req-uri-path']:
				# print(data['custom_fields'][activity_name+'_resp-header'])
				logout_errors[counter] =  ' Error: Request uri has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-uri-path']).startswith(" "):
				logout_errors[counter] =  " Request uri starts with whitespace, please remove it."
				counter +=1
		
		if data['custom_fields'][activity_name+'_req-params']:
			if '|' in data['custom_fields'][activity_name+'_req-params']:
				# print(data['custom_fields'][activity_name+'_resp-header'])
				logout_errors[counter] =  ' Error: Request params has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-params']).startswith(" "):
				logout_errors[counter] =  " Request params starts with whitespace, please remove it."
				counter +=1


			if any(x in str(data['custom_fields'][activity_name+'_req-params']).lower() for x in blacklist_words):
				logout_errors[counter] = " Error: Some of the blacklisted words are present in Request params"
				counter +=1

			if ',' in data['custom_fields'][activity_name+'_req-params']:
				req_params_comma_splitter = data['custom_fields'][activity_name+'_req-params'].split(",")
				for req_params_comma_split in req_params_comma_splitter:
					check_req_params = asterik_check(r"\*",str(req_params_comma_split))
					if check_req_params == True :
						logout_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
						counter +=1

			else:
				check_req_params = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-params']))
				if check_req_params == True :
					logout_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
					counter +=1


		# if data['custom_fields'][activity_name+'_response']:
		# 	# print(app_name)
		# 	logout_errors[counter] =" Response is filled, it should be empty"
		# 	counter +=1
			# print(login_loginFail_errors)

		if data['custom_fields'][activity_name+'_req-headers']:
			if  uri_pattern.match(data['custom_fields'][activity_name+'_req-headers']):
				logout_errors[counter] = ' Request header value seems to be incorrect (found same pattern as uri path)'
				counter +=1
						
			if '|' in data['custom_fields'][activity_name+'_req-headers']:
				# print(data['custom_fields'][activity_name+'_resp-header'])
				logout_errors[counter] =  ' Error: Request header has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-headers']).startswith(" "):
				logout_errors[counter] =  " Request header starts with whitespace, please remove it."
				counter +=1


			if any(x in str(data['custom_fields'][activity_name+'_req-headers']).lower() for x in blacklist_words):
				logout_errors[counter] = " Error: Some of the blacklisted words are present in Request header"
				counter +=1

			if ',' in data['custom_fields'][activity_name+'_req-headers']:
				req_header_comma_splitter = data['custom_fields'][activity_name+'_req-headers'].split(",")
				for req_header_comma_split in req_header_comma_splitter:
					check_req_head = asterik_check(r"\*",str(req_header_comma_split))
					if check_req_head == True :
						logout_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
						counter +=1


			else:
				check_req_head = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-headers']))
				if check_req_head == True :
					logout_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
					counter +=1

		if data['custom_fields'][activity_name+'_req-payload']:
			if  uri_pattern.match(data['custom_fields'][activity_name+'_req-payload']):
				logout_errors[counter] = ' Request payload value seems to be incorrect (found same pattern as uri path)'
				counter +=1

			if '|' in data['custom_fields'][activity_name+'_req-payload']:
				# print(data['custom_fields'][activity_name+'_resp-header'])
				logout_errors[counter] =  ' Error: Request payload has pipe symbol, please replace it with comma'
				counter +=1

			if str(data['custom_fields'][activity_name+'_req-payload']).startswith(" "):
				logout_errors[counter] =  " Request payload starts with whitespace, please remove it."
				counter +=1

			if any(x in str(data['custom_fields'][activity_name+'_req-payload']).lower() for x in blacklist_words):
				logout_errors[counter] = " Error: Some of the blacklisted words are present in Request payload"
				counter +=1

			if ',' in str(data['custom_fields'][activity_name+'_req-payload']):
				req_payload_comma_splitter = data['custom_fields'][activity_name+'_req-payload'].split(",")
				for req_payload_comma_split in req_payload_comma_splitter:
					check_req_pay = asterik_check(r"\*",str(req_payload_comma_split))
					if check_req_pay == True :
						logout_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
						counter +=1
			else:
				check_req_pay = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-payload']))
				if check_req_pay == True :
					logout_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
					counter +=1


	if (data['custom_fields'][activity_name+'_req-method'] == 'None') or (data['custom_fields'][activity_name+'_req-method'] == ''):
		logout_errors[counter] = "Request method is empty, it should be filled."
		counter += 1


	if (data['custom_fields'][activity_name+'_req-method'] == 'NA') or (data['custom_fields'][activity_name+'_req-method'] == 'REMAINING') :
		if not data['custom_fields'][activity_name+'_req-host'] and not data['custom_fields'][activity_name+'_req-uri-path'] and \
			not data['custom_fields'][activity_name+'_req-params'] and not data['custom_fields'][activity_name+'_req-headers'] and \
			not data['custom_fields'][activity_name+'_req-payload'] :
			pass
			# print(app_name)
			# print("all empty")
		else:
			logout_errors[counter] = "Request method is None but all fields are not empty"
			counter += 1

	
	return logout_errors, activity_present



def other_Acitivies_validation(data, activity_name, host_pattern, uri_pattern, other_activities_errors, activity_methods, blacklist_words):
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

			if '|' in data['custom_fields'][activity_name+'_req-host']:
				host_splitter = data['custom_fields'][activity_name+'_req-host'].split("|")

				for host_split in host_splitter:
					if not host_pattern.search(host_split):
						# print(":::::::::::::::::::::::")
						# print(host_pattern.search(data['custom_fields'][activity_name+'_req-host']))
						# print(data['custom_fields'][activity_name+'_req-host'])
						other_activities_errors[counter] = " Request host value seems to be incorrect"
						counter +=1


					if str(host_split).startswith(" "):
						other_activities_errors[counter] =  " Request host starts with whitespace, please remove it."
						counter +=1


					if any(x in str(host_split).lower() for x in blacklist_words):
						other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request host"
						counter +=1
					
					check_req_host = asterik_check(r"\*",str(host_split))
					if check_req_host == True :
						other_activities_errors[counter] = " Error: Asterik cannot be present in between request host value, please fix it"
						counter +=1

					if str(host_split).startswith("."):
						other_activities_errors[counter] = " Error: Asterik cannot be present in between request host value, please fix it"
						counter +=1




			else:

				if not host_pattern.search(data['custom_fields'][activity_name+'_req-host']):
					# print(":::::::::::::::::::::::")
					# print(host_pattern.search(data['custom_fields'][activity_name+'_req-host']))
					# print(data['custom_fields'][activity_name+'_req-host'])
					other_activities_errors[counter] = " Request host value seems to be incorrect"
					counter +=1


				if str(data['custom_fields'][activity_name+'_req-host']).startswith(" "):
					other_activities_errors[counter] =  " Request host starts with whitespace, please remove it."
					counter +=1


				if any(x in str(data['custom_fields'][activity_name+'_req-host']).lower() for x in blacklist_words):
					other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request host"
					counter +=1

				check_req_host = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-host']))
				if check_req_host == True :
					other_activities_errors[counter] = " Error: Asterik cannot be present in between request host value, please fix it"
					counter +=1

				if str(data['custom_fields'][activity_name+'_req-host']).startswith("."):
					other_activities_errors[counter] = " Error: Asterik cannot be present in between request host value, please fix it"
					counter +=1


		else:
			other_activities_errors[counter] = " Host is missing"
			counter +=1

		if data['custom_fields'][activity_name+'_req-uri-path']:

			if '|' in data['custom_fields'][activity_name+'_req-uri-path']:
				uri_splitter = data['custom_fields'][activity_name+'_req-uri-path'].split("|")
				for uri_split in uri_splitter:
					if not uri_pattern.match(uri_split):
							# print(data['custom_fields'][activity_name+'_req-uri-path'])
							other_activities_errors[counter] = " Request uri path value seems to be incorrect or starting '/' is missing(add /) or have space in starting(remove space)"
							counter +=1

					if str(uri_split).startswith(" "):
						other_activities_errors[counter] =  " Request uri starts with whitespace, please remove it."
						counter +=1

					if any(x in str(uri_split).lower() for x in blacklist_words):
						other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request uri"
						counter +=1


			else:
				if not uri_pattern.match(data['custom_fields'][activity_name+'_req-uri-path']):
					# print(data['custom_fields'][activity_name+'_req-uri-path'])
					other_activities_errors[counter] = " Request uri path value seems to be incorrect or starting '/' is missing(add /) or have space in starting(remove space)"
					counter +=1

				if str(data['custom_fields'][activity_name+'_req-uri-path']).startswith(" "):
					other_activities_errors[counter] =  " Request uri starts with whitespace, please remove it."
					counter +=1

				if any(x in str(data['custom_fields'][activity_name+'_req-uri-path']).lower() for x in blacklist_words):
					other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request uri"
					counter +=1

		if data['custom_fields'][activity_name+'_req-params']:	

			if '|' in data['custom_fields'][activity_name+'_req-params']:
				params_splitter = data['custom_fields'][activity_name+'_req-params'].split("|")
				for param_split in params_splitter:

					if uri_pattern.match(param_split):
							other_activities_errors[counter] = ' Params value seems to be incorrect (found same pattern as uri path)'
							counter +=1

					if any(x in str(param_split).lower() for x in blacklist_words):
						other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request params"
						counter +=1

					if str(param_split).startswith(" "):
						other_activities_errors[counter] =  " Request param starts with whitespace, please remove it."
						counter +=1
					
					if ',' in param_split:
						req_params_comma_splitter = param_split.split(",")
						for req_params_comma_split in req_params_comma_splitter:
							check_req_params = asterik_check(r"\*",str(req_params_comma_split))
							if check_req_params == True :
								other_activities_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
								counter +=1


					else:
						check_req_params = asterik_check(r"\*",str(param_split))
						if check_req_params == True :
							other_activities_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
							counter +=1


			else:

				if uri_pattern.match(data['custom_fields'][activity_name+'_req-params']):
					other_activities_errors[counter] = ' Params value seems to be incorrect (found same pattern as uri path)'
					counter +=1

				if any(x in str(data['custom_fields'][activity_name+'_req-params']).lower() for x in blacklist_words):
					other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request params"
					counter +=1

				if str(data['custom_fields'][activity_name+'_req-params']).startswith(" "):
					other_activities_errors[counter] =  " Request param starts with whitespace, please remove it."
					counter +=1
				
				if ',' in data['custom_fields'][activity_name+'_req-params']:
					req_params_comma_splitter = data['custom_fields'][activity_name+'_req-params'].split(",")
					for req_header_split in req_params_comma_splitter:
						check_req_params = asterik_check(r"\*",str(req_header_split))
						if check_req_params == True :
							other_activities_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
							counter +=1
				else:
					check_req_params = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-params']))
					if check_req_params == True :
						other_activities_errors[counter] = " Error: Asterik cannot be present in between request params value, please fix it"
						counter +=1

		if data['custom_fields'][activity_name+'_req-headers']:

			if "|" in data['custom_fields'][activity_name+'_req-headers']:
				req_head_splitter = data['custom_fields'][activity_name+'_req-headers'].split("|")

				for req_head_split in req_head_splitter:
					if  uri_pattern.match(req_head_split):
							other_activities_errors[counter] = ' Request header value seems to be incorrect (found same pattern as uri path)'
							counter +=1

					if any(x in str(req_head_split).lower() for x in blacklist_words):
						other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request header"
						counter +=1

					if str(req_head_split).startswith(" "):
						other_activities_errors[counter] =  " Request header starts with whitespace, please remove it."
						counter +=1
					if ',' in req_head_split:
						req_header_comma_splitter = req_head_split.split(req_head_split)
						for req_header_comma_split in req_header_comma_splitter:
							check_req_head = asterik_check(r"\*",str(req_header_comma_split))
							if check_req_head == True :
								other_activities_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
								counter +=1

					else:
						check_req_head = asterik_check(r"\*",str(req_head_split))
						if check_req_head == True :
							other_activities_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
							counter +=1

			else:

				if  uri_pattern.match(data['custom_fields'][activity_name+'_req-headers']):
					other_activities_errors[counter] = ' Request header value seems to be incorrect (found same pattern as uri path)'
					counter +=1

				if any(x in str(data['custom_fields'][activity_name+'_req-headers']).lower() for x in blacklist_words):
					other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request header"
					counter +=1

				if str(data['custom_fields'][activity_name+'_req-headers']).startswith(" "):
					other_activities_errors[counter] =  " Request header starts with whitespace, please remove it."
					counter +=1

				if ',' in data['custom_fields'][activity_name+'_req-headers']:
					req_header_comma_splitter =  data['custom_fields'][activity_name+'_req-headers'].split(",")
					for req_header_comma_split in req_header_comma_splitter:
						check_req_head = asterik_check(r"\*",str(req_header_comma_split))
						if check_req_head == True :
							other_activities_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
							counter +=1
				else:
					check_req_head = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-headers']))
					if check_req_head == True :
						other_activities_errors[counter] = " Error: Asterik cannot be present in between request header value, please fix it"
						counter +=1


		if data['custom_fields'][activity_name+'_req-payload']:
			if "|" in data['custom_fields'][activity_name+'_req-payload']:
				req_pay_splitter = data['custom_fields'][activity_name+'_req-payload'].split("|")
				
				for req_pay_split in req_pay_splitter:
					if uri_pattern.match(req_pay_split):
						# print(data['custom_fields'][activity_name+'_req-payload'])
						other_activities_errors[counter] = ' Request payload value seems to be incorrect (found same pattern as uri path)'
						counter +=1
					
					if str(req_pay_split).startswith(" "):
						other_activities_errors[counter] =  " Request payload starts with whitespace, please remove it."
						counter +=1

					if any(x in str(req_pay_split).lower() for x in blacklist_words):
						other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request payload"
						counter +=1

					if ',' in req_pay_split:
						req_pay_comma_splitter = req_pay_split.split(",")
						for req_pay_comma_split in req_pay_comma_splitter:
							check_req_pay = asterik_check(r"\*",str(req_pay_comma_split))
							if check_req_pay == True :
								other_activities_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
								counter +=1
					else:
						check_req_pay = asterik_check(r"\*",str(req_pay_split))
						if check_req_pay == True :
							other_activities_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
							counter +=1


			else:
				if uri_pattern.match(data['custom_fields'][activity_name+'_req-payload']):
					# print(data['custom_fields'][activity_name+'_req-payload'])
					other_activities_errors[counter] = ' Request payload value seems to be incorrect (found same pattern as uri path)'
					counter +=1
				
				if str(data['custom_fields'][activity_name+'_req-payload']).startswith(" "):
					other_activities_errors[counter] =  " Request payload starts with whitespace, please remove it."
					counter +=1

				if any(x in str(data['custom_fields'][activity_name+'_req-payload']).lower() for x in blacklist_words):
					other_activities_errors[counter] = " Error: Some of the blacklisted words are present in Request payload"
					counter +=1
				if ',' in data['custom_fields'][activity_name+'_req-payload']:
					req_header_comma_splitter = data['custom_fields'][activity_name+'_req-payload'].split(",")
					for req_header_comma_split in req_header_comma_splitter:
						check_req_pay = asterik_check(r"\*",str(req_header_comma_split))
						if check_req_pay == True :
							other_activities_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
							counter +=1
				else:
					check_req_pay = asterik_check(r"\*",str(data['custom_fields'][activity_name+'_req-payload']))
					if check_req_pay == True :
						other_activities_errors[counter] = " Error: Asterik cannot be present in between request payload value, please fix it"
						counter +=1
			

		# if data['custom_fields'][activity_name+'_response']:
		# 	# print(app_name)
		# 	other_activities_errors[counter] =" Response is filled, it should be empty"
		# 	counter +=1
		# 	# print(login_loginFail_errors)

	
	if (data['custom_fields'][activity_name+'_req-method'] == 'None') or (data['custom_fields'][activity_name+'_req-method'] == ''):
		other_activities_errors[counter] = "Request method is empty, it should be filled."
		counter += 1

	if (data['custom_fields'][activity_name+'_req-method'] == 'NA') or (data['custom_fields'][activity_name+'_req-method'] == 'REMAINING'):
		if not data['custom_fields'][activity_name+'_req-host'] and not data['custom_fields'][activity_name+'_req-uri-path'] and \
			not data['custom_fields'][activity_name+'_req-params'] and not data['custom_fields'][activity_name+'_req-headers'] and \
			not data['custom_fields'][activity_name+'_req-payload'] :
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


			# if data['custom_fields'][activity_name+'_response']:
			# 	value = data['custom_fields'][activity_name+'_response']
			# 	response_splitter = value.split('|')

			# 	if not (methods_ls_len == len(response_splitter)):
			# 		error_check = True


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


		# if data['custom_fields'][activity_name+'_response']:
		# 	value = data['custom_fields'][activity_name+'_response']
		# 	response_splitter = value.split('|')
		# 	values_length.append(len(response_splitter))
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
		if (validate_pcap+".saz" in attachments_names) or (validate_pcap+".SAZ" in attachments_names):
			pass
			# lst.append("Correct fileName")
		else:
			# print(validate_pcap)
			# print(attachments_names)
			lst.append("Incorrect fileName")
	elif activity_count > 0:
		for i in range(activity_count):
			validate_pcap = str(app_ticket)+"_"+activity_name+"-"+str(i)
			# print(validate_pcap)
			if (validate_pcap+".saz" in attachments_names) or (validate_pcap+".SAZ" in attachments_names):
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

blacklist_words = ['eitacies', 'smitht', 'test', 'cloudee', 'baladtrade', 'balad','demo', 'fiddler', 'cloudcentrique', 'centrique', 'rdymap']


def validate(data):
	error_logs = {}
	re_pattern_for_host = "(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
	host_pattern = re.compile(re_pattern_for_host)
	re_pattern_for_uri =r"(^\/.*)"
	uri_pattern = re.compile(re_pattern_for_uri)
	user = {}
	value = data
	# print(data)
	# print("_______________________________________")
	# print(data.values())
	# for app_name, value in data.items():

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
	# print(data["Status"])
	# print(value)
	# print(value['Status'])
	# print(type(value['Status']))

	if str(value['Status']) == 'Pcap Checks' or str(value['Status']) == 'Pcap Done' or str(value['Status']) == 'XML Done':
		initial_errors = initial_validation(value, initial_errors)

		activity_name = 'LOGIN'
		login_errors, activity_flag = login_and_login_fail_validation(value, activity_name, host_pattern, uri_pattern,login_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		login_depth_lst = login_and_login_fail_depth(value, activity_name, login_depth_lst)
		login_acitivty_count = 1
		if activity_flag:
			login_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], login_acitivty_count-1)
		# print("Login depth")
		# print(login_depth_lst )

		activity_name = 'LOGIN-FAIL'
		loginFail_errors, activity_flag = login_and_login_fail_validation(value, activity_name, host_pattern, uri_pattern, loginFail_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		loginFail_depth_lst = login_and_login_fail_depth(value, activity_name, loginFail_depth_lst)
		loginFail_acitivty_count = 1
		if activity_flag:
			loginFail_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], loginFail_acitivty_count-1)
		# print("Login-fail depth")
		# print(loginFail_depth_lst)
		# print((login_depth_lst))
		# print((loginFail_depth_lst))
		# if login_depth_lst == loginFail_depth_lst:
		# 	print('yesss')
		# print(login_depth_lst)
		depth = ""
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
		logout_errors, activity_flag = logout_validation(value, activity_name, host_pattern, uri_pattern, logout_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		logout_acitivty_count = 1
		if activity_flag:
			logout_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], logout_acitivty_count-1)
		# print(logout_errors)


		activity_name = 'UPLOAD'
		upload_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, upload_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		upload_multiple_methods_err, upload_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, upload_multiple_methods_err,upload_multiple_methods_err_lst, activity_methods)
		upload_multiple_values_err, upload_values_count = multiple_values_validation(value, activity_name, upload_multiple_values_err)
		if activity_flag:
			upload_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], upload_values_count-1)



		activity_name = 'DOWNLOAD'
		download_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, download_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		download_multiple_methods_err, download_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, download_multiple_methods_err, download_multiple_methods_err_lst, activity_methods)
		download_multiple_values_err, download_values_count = multiple_values_validation(value, activity_name, download_multiple_values_err)
		if activity_flag:
			download_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], download_values_count-1)

		# print(download_multiple_methods_err)
		activity_name = 'DELETE'
		delete_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, delete_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		delete_multiple_methods_err, delete_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, delete_multiple_methods_err,  delete_multiple_methods_err_lst, activity_methods)
		delete_multiple_values_err, delete_values_count = multiple_values_validation(value, activity_name, delete_multiple_values_err)
		if activity_flag:
			delete_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], delete_values_count-1)


		# print(delete_multiple_methods_err)

		
		activity_name = 'SHARE'
		share_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, share_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		share_multiple_methods_err, share_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, share_multiple_methods_err,  share_multiple_methods_err_lst, activity_methods)
		share_multiple_values_err, share_values_count = multiple_values_validation(value, activity_name, share_multiple_values_err)
		if activity_flag:
			share_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], share_values_count-1)

		# print(share_multiple_methods_err)

		activity_name = 'READ-ONLY'
		readonly_errors, activity_flag = other_Acitivies_validation(value, activity_name, host_pattern, uri_pattern, readonly_errors, activity_methods, blacklist_words)
		activies_present.append(activity_flag)
		readonly_multiple_methods_err, readonly_multiple_methods_err_lst = multiple_methods_validation(value, activity_name, readonly_multiple_methods_err, readonly_multiple_methods_err_lst, activity_methods)
		readonly_multiple_values_err, readonly_values_count = multiple_values_validation(value, activity_name, readonly_multiple_values_err)
		if activity_flag:
			readonly_file_error = attachment_names_validation(value['Attachments_list'], activity_name, data["Ticket_number"], readonly_values_count-1)
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
			errors_dict['DELETE-Filename-Error'] = delete_file_error

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
			error_logs[value['Summary']+" "+value['custom_fields']["_Product_id"]] = errors_dict

		

		print("Validating data... Please wait!!")
		return error_logs
	else:
		messagebox.showerror(title="Incorrect status", message='Error!! App is not in Status "Pcap done!!"')
		print('Error!! App is not in Status "Pcap done!!"')
		error_logs = "Not_performed"
		return error_logs
		

# with open('assembla_data') as f:
#   data = json.load(f)


def validate_on_click():
			splitted_txt = []
	# try:
			# To get data from assembla
			space_name='Granular Controls'
			my_space= assembla.spaces(name=space_name)[0]
			#print(len(my_space.tickets()))
			#below method call to hit the assembla api
			gc = txt.get().strip()
			if ',' in gc:
				splitted_txt = gc.split(",")
			else:
				splitted_txt.append(int(gc))
			data = assembla_data_to_json( splitted_txt, my_space, my_headers)
			# print(data)
			# print("******************************************************")


			for single_value in splitted_txt:

				if type(int(str(single_value).strip())) == int:
					number = int(single_value)
					result = validate(data[str(single_value)])
					if result:
						if result != "Not_performed":
							#messagebox.showwarning(title="Errors found", message="Errors Found in your app!! please check the saved json.")
							print("Errors Found in your app !! please check the saved json..")
							print("Done processing...")
							with open(single_value+'_errors.json', 'w') as outfile:
								json.dump(result, outfile,indent=4)
						else:
							print("Assembla Status Error!")
					else:		
						#messagebox.showinfo(title="No Errors", message="Congratulations, No Errors found...")
						print("Congratulations, No Errors found...")
						print("Done processing...\n")
						# break
					print("----------------------------Result for GC- ",single_value,"-----------------------------")
					print(result)
					print("----------------------------------------------------------------------------------------")
			print("\n\n********************** Done Validation For All GC- :", splitted_txt," **********************")
					
	







window = Tk()
window.title("Validate Assembla Data")
# Gets the requested values of the height and widht.
windowWidth = window.winfo_reqwidth()
windowHeight = window.winfo_reqheight()

# Gets both half the screen width/height and window width/height
positionRight = int(window.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(window.winfo_screenheight()/2 - windowHeight/2)

# Positions the window in the center of the page.

window.geometry("+{}+{}".format(positionRight, positionDown))

lbl = Label(window, text="Please enter GC-codes to validate your apps ", font=("Arial Bold", 12))
lbl.grid(column=1, row=0, padx=10, pady=10)


txt = Entry(window,width= 50)
txt.grid(column=1, row=2,padx=10, pady=10)



btn = Button(window, text="          Validate          ", command=validate_on_click, font=("Arial", 10), bg='Green', fg='white')
btn.grid(column=1, row=3, padx=10, pady=10)


lbl2 = Label(window, text="Note: For multiple apps, use comma as a separator between GC-Codes", font=("Arial", 9), bg='light blue',foreground="Blue")
lbl2.grid(column=1, row=4, padx=10, pady=10)


window.bind('<Return>', lambda event=None: btn.invoke())
window.configure(bg="light blue",relief=RAISED, cursor='gumby')
window.mainloop()
























