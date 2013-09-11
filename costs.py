
import requests
import json



def get_price(size):
    return size['valueColumns'][0]['prices']['USD']

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
        pricing_data[region['region']] = value
    return pricing_data
    
def main():
    pricing_data = fetch_pricing_data()
    
    with open('aws.json') as fd:
        aws = json.load(fd)
    instance_types = aws['services']['Elastic Compute Cloud']['instance_types']
    
    from itertools import groupby
    keyfunc = lambda key: key[1]['category']
    sgroupby = lambda iterable, keyfunc: groupby(sorted(iterable, key=keyfunc), keyfunc)
    
    region_pricing = pricing_data['us-east']
    print 
    for cetegory, instance_types in sgroupby(instance_types.items(), keyfunc):
        print cetegory
        for instance_id, ity in instance_types:
            print '+ %s (%s)' % (ity['name'], instance_id),
            print region_pricing[ity['type']][ity['size']]
        print 
    
    
if __name__ == '__main__':
    main()
