from django.shortcuts import render, redirect
from flutterwave import Flutterwave
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages

from general import flw, api_key, merchant_key, generate_ref_no, keep_values, clear_values_from_session, \
                    get_countries

            
            
def initiate(request):
    '''Verify'''
    
    if request.method == "POST":
        #print request.POST
        print 'posting to verify card'
                
        payload = request.POST.copy()
        payload.update({"customerID": "cust1471629671",
                    'responseUrl': reverse('payment:tok_initiate')})
        payload.pop('csrfmiddlewaretoken')
        
        bvn_or_pin = False
        if payload['authModel'] == ('BVN' or 'PIN'):
            bvn_or_pin = True
        
        #print 'data: ',data
        
        verify                  = flw.card.tokenize(payload)
        verify_json             = verify.json()
        
        #print 'verify_json: ',verify_json
        response_data = verify_json['data']
        
        if response_data.has_key('responsemessage'):
            responseMessage         = response_data['responsemessage']
            messages.error(request, '%s' %responseMessage)
        
        if verify_json['status'] != 'error':
            
            response_data.update({'country': payload['country']})
            #print 'response_data: ',response_data
            responsecode = response_data['responsecode']
            if responsecode == '02':
                keys_list = ['otptransactionidentifier', 'transactionreference', 'country']
                keep_values(request, keys_list, response_data)
                
                if bvn_or_pin == True:
                    #return redirect(reverse('payment:tok_enter_otp'))
                    return redirect(reverse('enter_otp'))
        else:
            responseMessage = verify_json['status']
            messages.error(request, '%s' %responseMessage)
            
    months = []
    for i in range(1, 13):
        months.append(str(i).zfill(2))
    
    years = []
    for i in range(6):
        years.append(str(2016+i))
    
    return render(request, 'tokenize_card/initiate.html', {'months': months, 'years': years,
                                                           'countries': get_countries()})
    


def transaction_result(request):
    context = {}
    '''Validate Transaction'''
    if request.method == "POST":
        data = request.POST.copy()
                
        verify                  = flw.card.validate(data)
        verify_json             = verify.json()
        
        #otp = request.POST.get('otp')
        response_data = verify_json['data']
        
        #responseMessage = response_data['responsemessage']
        #messages.error(request, '%s' %responseMessage)
            
        # '''Retrieve saved values from session'''
        # api_key, merchant_key, verifyUsing, country, transactionReference, bvn  = retrieve_values(request)           
        # 
        # flw                                     = initialize_flw(api_key, merchant_key)
        # validate                                = flw.bvn.validate(bvn, otp, transactionReference, country)
        # validate_json                           = validate.json()
        # 
        # print 'validate_json: ',validate_json
        
        context.update({'data': response_data, 'tokenize_card': 'tokenize_card'})
                
        '''Clear saved values from session'''
        keys_list = ['otptransactionidentifier', 'transactionreference', 'country']
        clear_values_from_session(request, keys_list)

        
        return render(request, 'result.html', context)
    
    return redirect(reverse('payment:tok_initiate'))
    