from django.shortcuts import render
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
from django.http import HttpResponse
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from paytm import Checksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'
# Create your views here.
def index(request):
    # products = Product.objects.all()
    # print(products)
    #  n = len(products)

    # nSlides = n//4 + ceil((n/4)-(n//4))

    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1, nSlides), nSlides])
    #params = {'no_of_slides':nSlides, 'range': range(1,nSlides),'product': products}
    #allProds = [[products, range(1, nSlides), nSlides],
    #            [products, range(1, nSlides), nSlides]]
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        print(request)
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        contact = Contact(name=name, email=email, phone=phone, message=message,date=datetime.now())
        contact.save()
        thank = True
        id = contact.msg_id
        return render(request, 'shop/contact.html',{'thank':thank, 'id':id})
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/search.html')

def searchMatch(query, item):
    '''Return True only if querry matches'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        if len(prod) != 0:
            allProds.append([prod,range(1, nSlides), nSlides])
    #params = {'no_of_slides':nSlides, 'range': range(1,nSlides),'product': products}
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query) < 3:
        params = {'msg': "No Results - Please make sure to enter relevant search query"}

    return render(request, 'shop/search.html', params)


def products(request, myid):
    # Fetch the product using Id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/product.html',  {'product':product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsjson')
        amount = int(request.POST.get('amount'))
        name = request.POST.get('iname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address1', '')+ " " + request.POST.get('address1', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        order = Orders(items_json=items_json, amount=amount, name=name, email=email, phone=phone, address=address, city=city, state=state, zip_code=zip_code, date=datetime.now())
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        pay_type = request.POST.get('pay_type')
        thankyou = True
        id = order.order_id
        if pay_type:
            return render(request, 'shop/checkout.html', {'thank':thankyou, 'id': id})
        else:
            #Request paytm to transfer the amount to your account after payment by user
            param_dict = {
                'MID':'WorldP64425807474247',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

            }
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
            return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})


def cart(request):
    return render(request, 'shop/checkout.html')

