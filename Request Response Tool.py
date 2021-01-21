from tkinter.constants import DISABLED
import PySimpleGUI as sg
import requests
import json
import os

os.makedirs('JSON Files', exist_ok=True)
os.chdir(os.getcwd() + '\\JSON Files')
path = os.getcwd()
# print('Created Path: ', path)
offerID = 0
spec = []
offer_list = []

def updateCart():
    pass



layout1 = [
    [sg.Text('Street Name*', size=(11, 1)), sg.InputText(key='-STREET-', size=(25, 1))],
    [sg.Text('Apt Num', size=(11, 1)), sg.InputText(key='-APT-', size=(25, 1))],
    [sg.Text('Zip Code*', size=(11, 1)), sg.InputText(key='-ZIP-', size=(25, 1))],
    [sg.Text('Promotion', size=(11, 1)), sg.Radio('TRUE', group_id=1, default=True, key='true', size=(5, 1)), sg.Radio('FALSE', group_id=1, key='false', size=(5, 1))],
    [sg.Text('Channel', size=(11, 1)), sg.Radio('DSA', group_id=2, default=True, key='DSL', size=(5, 1)), sg.Radio('ISA', group_id=2, key='ISA', size=(5, 1))],
    [sg.Text('Environment', size=(11, 1)), sg.Radio('UAT', group_id=3, default=True, key='', size=(5, 1)), sg.Radio('UAT1', group_id=3, key='/uat1', size=(5, 1)), sg.Radio('UAT2', group_id=3, key='/uat2', size=(5, 1))],
    [sg.Text(size=(1, 1)), sg.Button('Submit', key='-SUBMIT-', size=(15, 1)), sg.Button('Update Shopping Cart?', key='-UPDATECART-', disabled=True)],
    [sg.Text(size=(9, 1)), sg.Button('Open Folder', key='-FOLD-', size=(15, 1))]

]

layout2 = [
    [sg.Text('Select Offer', size=(11, 1)), sg.Combo(offer_list, key='offerID', size=(50, 1))],
    [sg.Text('Enter Services', size=(11, 1)), sg.InputText(key='services', size=(25, 1)), sg.Text('((?))', tooltip='Enter comma-separated, non-spaced Rate Codes.\nDo this if you want any of the Rate Code to be "isAssigned: true" in the EPC response.\nLeave this blank if not sure.')],
    [sg.Text(size=(11, 1)), sg.Button('Back', key='-BACK-', size=(12, 1)), sg.Button('Update Cart', key='-UPDATE-', size=(12, 1)), sg.Button('Open Folder', key='-FOLD1-', size=(12, 1))]
]

layout = [
    [sg.Column(layout1, key='-COL1-'),
    sg.Column(layout2, key='-COL2-', visible=False)]
]
window = sg.Window('Request Reponse', layout)

url1 = 'https://ws-uat.suddenlink.cequel3.com'
url_findAddress = '/optimum-ecomm-abstraction-ws/rest/uow/findAddress'
url_createShoppingCart = '/optimum-ecomm-abstraction-ws/rest/uow/createShoppingCart'
url_searchProductOffering = '/optimum-ecomm-abstraction-ws/rest/uow/searchProductOffering'
url_updateShoppingCart = '/optimum-ecomm-abstraction-ws/rest/uow/updateShoppingCart'

while True:
    event, values = window.Read()
    print(f'Event: {event} | Values: {values}')
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    
    if event == '-SUBMIT-':
        offer_list = []
        street = values['-STREET-'].upper()
        apt = values['-APT-']
        zip = values['-ZIP-']
        if street == "" or zip == "":
            sg.PopupError("Street and Zip Code are mandatory!")
        elif not zip.isdigit():
            sg.PopupError("Zip Code should be numeric value!")
        elif len(zip) > 5:
            sg.PopupError("Zip Code length should not exceed 5 digits!")
        else:
            lst = [k for k, v in values.items() if v == True]
            promo, channel, env = lst
            url_fa = url1 + env + url_findAddress
            # print(f'URL Find Address: {url_fa}')


            findAddress_payload = f'''{{"address1" : "{street}", "address2": "{apt}", "zip" : "{zip}"}}'''
            findAddress_request = json.loads(findAddress_payload)
            try:
                findAddress_response = requests.post(url_fa, json=findAddress_request, verify=False).json()
            except:
                sg.PopupError("Network Issue or Altice VPN not connected!")
            else:
                # print(json.dumps(findAddress_response, indent=4))

                with open('findAddress_request.json', 'w+', encoding='utf-8') as fa_req:
                    fa_req.write(json.dumps(findAddress_request, indent=4))

                with open('findAddress_response.json', 'w+', encoding='utf-8') as fa_res:
                    fa_res.write(json.dumps(findAddress_response, indent=4))
                try:
                    add_list = findAddress_response["detailedAccounts"][0]
                    # print(add_list)
                except IndexError:
                    sg.PopupError('Invalid Address')
                else:
                    ftax = add_list["ftax"]
                    city = add_list["service_city"]
                    state = add_list["service_state"]
                    cluster = add_list["clust"]
                    market = add_list["mkt"]
                    corp = add_list["corp"]
                    house = add_list["house"]
                    cust = add_list["cust"]
                    try:
                        eid = add_list["eligibilityId"]
                    except KeyError:
                        eid = ''
                    url_csc = url1 + env + url_createShoppingCart
                    # print(f'URL Find Address: {url_csc}')
                    # print(ftax, city, state, cluster, market, corp, house, cust, eid)

                    createShoppingCart_payload = f'''{{"customerType":"R","isCommercialAccept":false,"serviceAddress":{{"apt":"{apt}","fta":"{ftax}","street":"{street}","city":"{city}","state":"{state}","zipcode":"{zip}","type":"","clusterCode":"{cluster}","mkt":"{market}","corp":"{corp}","house":"{house}","cust":"{cust}"}},"locale":"en_US"}}'''
                    createShoppingCart_request = json.loads(createShoppingCart_payload)
                    
                    createShoppingCart_response = requests.post(url_csc, json=createShoppingCart_request, verify=False).json()

                
                    # print(json.dumps(createShoppingCart_response, indent=4))

                    with open('createShoppingCart_request.json', 'w+', encoding='utf-8') as csc_req:
                        csc_req.write(json.dumps(createShoppingCart_request, indent=4))

                    with open('createShoppingCart_response.json', 'w+', encoding='utf-8') as csc_res:
                        csc_res.write(json.dumps(createShoppingCart_response, indent=4))

                    cartID = createShoppingCart_response["createShoppingCartRESTReturn"]["cartId"]
                    # print(f'Cart ID: {cartID}')

                    url_prdOff = url1 + env + url_searchProductOffering
                    # print(f'URL Find Address: {url_prdOff}')

                    searchProductOffering_payload = f'''{{"salesContext":{{"localeString":"en_US","salesChannel":"{channel}"}},"searchProductOfferingFilterInfo":{{"oolAvailable":true,"ovAvailable":true,"ioAvailable":true,"includeExpiredOfferings":false,"salesRuleContext":{{"customerProfile":{{"anonymous":true}},"customerInfo":{{"customerType":"R","newCustomer":true,"orderType":"Install","isPromotion":{promo},"eligibilityID":"{eid}"}}}},"eligibilityStatus":[{{"code":"EA"}}]}},"offeringReadMask":{{"value":"SUMMARY"}},"checkCustomerProductOffering":false,"locale":"en_US","cartId":"{cartID}","serviceAddress":{{"apt":"{apt}","fta":"{ftax}","street":"{street}","city":"{city}","state":"{state}","zipcode":"{zip}","type":"","clusterCode":"{cluster}","mkt":"{market}","corp":"{corp}","house":"{house}","cust":"{cust}"}},"generics":false}}'''
                    # print(searchProductOffering_payload)
                    searchProductOffering_request = json.loads(searchProductOffering_payload)
                    
                    searchProductOffering_response = requests.post(url_prdOff, json=searchProductOffering_request, verify=False).json()
                    offers = searchProductOffering_response["searchProductOfferingReturn"]["productOfferingResults"]

                    for x in offers:
                        offer_list.append(x["matchingProductOffering"]["ID"] + '-' + x["matchingProductOffering"]["title"])
                    # print(offer_list)

                    with open('searchProductOffering_request.json', 'w+', encoding='utf-8') as spo_req:
                        spo_req.write(json.dumps(searchProductOffering_request, indent=4))

                    with open('searchProductOffering_response.json', 'w+', encoding='utf-8') as spo_res:
                        spo_res.write(json.dumps(searchProductOffering_response, indent=4))

                    prompt = sg.PopupOK('Done, request response files created.', title='Success')
                
                    window['-UPDATECART-'].update(disabled=False)
                    window['offerID'].update(values = offer_list)

    if event in ('-FOLD-', '-FOLD1-'):
        os.startfile(path)


    if event == '-UPDATECART-':
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=True)

    if event == '-BACK-':
        window['-COL1-'].update(visible=True)
        window['-COL2-'].update(visible=False)


    if event == '-UPDATE-':
        for x in offers:
            if values['offerID'].split('-')[0] == x["matchingProductOffering"]["ID"]:
                spec = [y["productSpecs"][0]["ID"] for y in x["matchingProductOffering"]["productOfferingProductSpecs"]]
                offerID = x["matchingProductOffering"]["ID"]
                offerName = x["matchingProductOffering"]["title"]
                # print(offerID, offerName, spec)
                # of_tup = (offerID, offerName, spec)
                if len(spec) == 1:
                    prod_to_conf = f'''{{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[0]}"}}}}'''
                if len(spec) == 2:
                    prod_to_conf = f'''{{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[0]}"}}}}, {{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[1]}"}}}}'''
                if len(spec) == 3:
                    prod_to_conf = f'''{{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[0]}"}}}}, {{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[1]}"}}}}, {{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[2]}"}}}}'''

                if values['services']:
                    service = json.dumps(list(values['services'].split(',')))
                else:
                    service = []
                url_usc = url1 + env + url_updateShoppingCart
                updateShoppingCart_payload = f'''{{"cartId":"{cartID}","isCheckEligibility":false,"productsToConfigure":[{prod_to_conf}],"ruleExecutionContext":{{"customerInfo":{{"customerType":"R","newCustomer":true}},"customerProfile":{{"anonymous":true}},"isOffline":false,"isFullXml":true,"productInfo":{{"services":{service}}}}},"saleContext":{{"localeString":"en_US","salesChannel":"{channel}"}},"locale":"en_US","serviceAddress":{{"zipcode":"{zip}","fta":"{ftax}","corp":"{corp}","city":"{city}","street":"{street}","mkt":"{market}","clusterCode":"{cluster}","state":"{state}","house":"{house}","cust":"{cust}"}}}}'''
                updateShoppingCart_request = json.loads(updateShoppingCart_payload)
                # print(json.dumps(updateShoppingCart_request, indent = 4))
                updateShoppingCart_response = requests.post(url_usc, json=updateShoppingCart_request, verify=False).json()

                with open(f'{offerID}_{offerName}_request.json', 'w+', encoding='utf-8') as usc_req:
                    usc_req.write(json.dumps(updateShoppingCart_request, indent=4))

                with open(f'{offerID}_{offerName}_response.json', 'w+', encoding='utf-8') as usc_res:
                    usc_res.write(json.dumps(updateShoppingCart_response, indent=4))

                prompt = sg.PopupOK('Done, Shopping cart updated.', title='Success')



window.close()