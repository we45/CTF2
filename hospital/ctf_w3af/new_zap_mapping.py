es = Elasticsearch()
init_es = {}
init_es['vulnerability'] = {}
data = new.get_results()
json_db = json.dumps(data, indent=4)
vul_data = json.loads(json_db)
for k, v in vul_data.items():
    alert = v.get('alert')
    if isinstance(alert, dict):
        std_es = init_es
        std_es['vulnerability'] = {
            'tool': 'ZAP',
            'name': alert.get('alert', 'Unknown'),
            'created_on': datetime.now().strftime("%Y-%m-%d"),
            'description': alert.get('description', ''),
            'remediation': alert.get('solution', ''),
            'severity': severity_dict.get(alert.get('risk', 'Info'), 0)
        }
        request_string = "%s%s" % (v.get('requestHeader', ''), v.get('requestBody', ''))
        response_string = "%s%s" % (v.get('responseHeader', ''), v.get('responseBody', ''))
        cwe = v.get('cweid')
        if cwe:
            std_es['vulnerability']['cwe'] = {
                'cwe_id': cwe,
                'cwe_link': 'https://cwe.mitre.org/top25/index.html#CWE-%s' % cwe
            }
        std_es['vulnerability']['app_param'] = {
            'param_name': alert.get('param', ''),
            'param_url': alert.get('url', ''),
            'param_request': base64.b64encode(request_string),
            'param_response': base64.b64encode(response_string)
        }
        std_es['vulnerability']['evidences'] = {
            'log': base64.b64encode(alert.get('evidence', ''))
        }
        es.index(index='ctf', doc_type='zap_docs', body=std_es)