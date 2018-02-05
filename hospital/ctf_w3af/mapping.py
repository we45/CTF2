scan_urls = '{0}/scans/{1}/kb/'.format(W3AF_URL,scan_id)
		r = requests.get(scan_urls)
		ids = json.loads(r.text).get('items')
		unique_vuls = {i.get('name'):[] for i in ids}
		for j in ids:
			unique_vuls[j.get('name')].append(j.get('id'))
		for vuls in unique_vuls.values():
			init_es = {}
			init_es['vulnerability'] = {}
			std_es = init_es
			req_url = '{0}/scans/{1}/kb/{2}'.format(W3AF_URL,scan_id,vuls[-1])
			req = requests.get(req_url)
			req_value = json.loads(req.text)
			for i in vuls:
				req_url = '{0}/scans/{1}/kb/{2}'.format(W3AF_URL,scan_id,i)
				req_value = json.loads(req.text)
				req_resp = requests.get('{0}{1}'.format(W3AF_URL,req_value.get('traffic_hrefs')[0]))
				req_json = json.loads(req_resp.text)
            std_es['vulnerability'] = {
				'tool' : 'w3af',
                'name': req_value.get('name', 'Unknown'),
				'created_on': datetime.now().strftime("%Y-%m-%d"),
				'description' : req_value.get('long_description',''),
				'remediation' : req_value.get('fix_guidance',''),
				'severity' : severity_dict.get(req_value.get('severity','Information'))
			}
            cwe = req_value.get('cwe_ids')
            if cwe and isinstance(cwe, list) and len(cwe):
                std_es['vulnerability']['cwe'] = {
                    'cwe_id': cwe[0],
                    'cwe_link': 'https://cwe.mitre.org/top25/index.html#CWE-%s' % cwe[0]
                }
			std_es['vulnerability']['app_param'] = {
                'param_name': req_value.get('var', ''),
                'param_url': req_value.get('url', ''),
                'param_request': req_json.get('request', ''),
                'param_response': req_json.get('response', ''),
            }
            std_es['vulnerability']['evidences'] = {
                'log': req_value.get('evidence','')
            }
			es.index(index = 'ctf', doc_type='w3af_docs', body = std_es, request_timeout=60)
