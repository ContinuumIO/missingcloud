
import requests
import json
import sys

RMAP = {'us-east':'us-east-1', 
        'us-west-2':'us-west-2',
        'us-west':'us-west-1', 
        'eu-ireland':'eu-west-1', 
        'apac-sin':'ap-southeast-1', 
        'apac-tokyo':'ap-northeast-1', 
        'apac-syd':'ap-southeast-2', 
        'sa-east-1':'sa-east-1',
        }


def get_price(size):
    price = size['valueColumns'][0]['prices']['USD']
    if price == 'N/A':
        return None
    return float(price)

def mktype(ty):                           
    if ty.endswith('ODI'):
        return ty[:-3]
    elif ty.endswith('I'):
        return ty[:-1]
    raise Exception(ty)

def fetch_pricing_data():
    res = requests.get('http://aws.amazon.com/ec2/pricing/json/linux-od.json')
    data = res.json()
    
    pricing_data = {} 
    for region in data['config']['regions']:
        instanceTypes = region['instanceTypes']
        value = {mktype(ity['type']):{size['size']:get_price(size) for size in ity['sizes']} for ity in instanceTypes}
        pricing_data[RMAP[region['region']]] = value
    return pricing_data
    
def main():
    pricing_data = fetch_pricing_data()
    
    with open('aws.json') as fd:
        aws = json.load(fd)
    instance_types = aws['services']['Elastic Compute Cloud']['instance_types']
    
    from itertools import groupby
    keyfunc = lambda key: key[1]['category']
    sgroupby = lambda iterable, keyfunc: groupby(sorted(iterable, key=keyfunc), keyfunc)
    
    
    print 
    for cetegory, instance_types in sgroupby(instance_types.items(), keyfunc):
        print cetegory
        for instance_id, ity in instance_types:
            col1 = '%s (%s)' % (ity['name'], instance_id)
            print ' + %-35s' %(col1,),
            for region in sys.argv[1:]:
                region_pricing = pricing_data.get(region,{})
                cost = region_pricing.get(ity['type'],{}).get(ity['size'])
                if cost:
                    col2 = '$%.3f / hour' % region_pricing.get(ity['type'],{}).get(ity['size'])
                else:
                    col2 = 'unavailable'
                print ' | %15s' % col2,
            print 
        print 
    
    
if __name__ == '__main__':
    main()
