##import modules if not found#######

import cx_Oracle,datetime,time
import requests,json

today = datetime.date.today()
openbracket = "("
closebracket = ")"

start = time.time()

try:
    dsn_tns = cx_Oracle.makedsn('XXX-XXXX-XXX-XX-XXX', '1521', service_name='sit105')
    conn = cx_Oracle.connect(user='XXXXXXXX', password='XXXXXXXX', dsn=dsn_tns)
    c = conn.cursor()
    c.execute("""select salestransactionseq as seq from cs_salestransaction where compensationdate >= '01-Dec-2019'""")
    result = c.fetchall()
    
    end = time.time() 
    print("Time consumed: {} secs".format(end-start))
    
    print('The count of seq is as on:', len(result))
    #print(result)
      
    
    
    
 ### exception handling ######       
    
    x = 14636698808889076
    
except cx_Oracle.DatabaseError as e:
    print("There is a problem with Oracle", e)
    conn.close()
    
'''

env = "https://XXXX-env.callidusondemand.com/api/v2/"
endpoint = "salesTransactions"
headers = {
    'authorization': "Basic XXXXXXXXXXXXXXXX==",
    'cache-control': "no-cache"
    }

print(x)

response = requests.request("DELETE", env+endpoint+openbracket+str(x)+closebracket, headers=headers)
print(response)
response.encoding = 'utf-8' 
response.text
response.json()
    
'''



