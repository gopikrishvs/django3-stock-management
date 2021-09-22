from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib import messages
import csv
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Count,Sum

@login_required
def home(request):
    title = 'This is Homepage'
    stocks = Category.objects.all()
    categ2 = [{"title":cat.name, "count":Stock.objects.filter(category=cat).count()} for cat in Category.objects.all()]

    cat = Category.objects.annotate(stocksum=Sum('stock__quantity'))
    categ = [{"title":c.name, "count":c.stocksum} for c in cat]
    context = {
        'title' : title,
        'stocks' : stocks,
        'categ' : categ,
        'categ2' : categ2,
    }
    return render(request,'home.html',context)

def register(request):
    title = 'Register'
    if request.method == 'POST':  
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request,'Registration Successful')
            return redirect('home')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = CreateUserForm()
    context = {
        'form' : form,
        'title' : title
    }

    return render(request,'register.html', context)

@login_required
def list_items(request):
    title = 'List of Items'
    form = StockSearchForm(request.POST or None)
    queryset = Stock.objects.all()
    context = {
        'header' : title,
        'queryset' : queryset,
        "form": form
        }
    
    if request.method == 'POST':
        category = form['category'].value()
        queryset = Stock.objects.filter(
                                item_name__icontains=form['item_name'].value()
                                )
        if (category != ''):
            queryset = queryset.filter(category_id=category)
        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
            writer = csv.writer(response)
            writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
            instance = queryset
            for stock in instance:
                writer.writerow([stock.category, stock.item_name, stock.quantity])
            return response

        context = {
        "form": form,
        "header": title,
        "queryset": queryset,
    }       
    
    return render(request,'list_items.html',context)

@login_required
def add_items(request):
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Item added')
        return redirect('/list_items')
    context = {
        'form' : form,
        'title' : 'Add Items'
    }
    return render(request,'add_items.html',context)

@login_required
def update_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = StockUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item Updated')
            return redirect('/list_items')
    context = {
        'form' : form
    }
    return render(request,'add_items.html',context)

@login_required
def delete_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    it_name = get_object_or_404(Stock, id=pk)
    if request.method == 'POST':
        queryset.delete()
        messages.success(request, 'Item deleted')
        return redirect('/list_items')
    context = {
        'item':it_name
        }
    return render(request, 'delete_items.html', context)

@login_required
def stock_detail(request, pk):
    queryset = Stock.objects.get(id=pk)
    context = {
		"title": queryset.item_name,
		"queryset": queryset,
	}
    return render(request, "stock_detail.html", context)

@login_required
def issue_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.received_quantity = 0
        instance.quantity -= instance.issue_quantity
        instance.issue_by = str(request.user)
        messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + " left")
        instance.save()
        return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": 'Issue ' + str(queryset.item_name),
        "queryset": queryset,
        "form": form,
        "username": 'Issue By: ' + str(request.user),
    }
    return render(request, "add_items.html", context)


@login_required
def receive_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.issue_quantity = 0
        instance.quantity += instance.received_quantity
        instance.received_by = str(request.user)
        instance.save()
        messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name)+" added")

        return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())
    context = {
            "title": 'Receive ' + str(queryset.item_name),
            "instance": queryset,
            "form": form,
            "username": 'Receive By: ' + str(request.user),
        }
    return render(request, "add_items.html", context)

@login_required
def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))
        return redirect("/list_items")
    context = {
            "instance": queryset,
            "form": form,
        }
    return render(request, "add_items.html", context)

@login_required
def list_history(request):
    header = 'HISTORY'
    form = StockHistorySearchForm(request.POST or None)
    queryset = StockHistory.objects.all()
    context = {
        "header": header,
        "queryset": queryset,
        "form": form
    }
    
    if request.method == 'POST':
        category = form['category'].value()
        queryset = StockHistory.objects.filter(
                item_name__icontains=form['item_name'].value(),
                last_updated__range=[
                    form['start_date'].value(),
                    form['end_date'].value()
                    ]
            )
        if (category != ''):
            queryset = queryset.filter(category_id=category)
            
        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            writer = csv.writer(response)
            writer.writerow(
                ['CATEGORY', 
                'ITEM NAME',
                'QUANTITY', 
                'ISSUE QUANTITY', 
                'RECEIVED QUANTITY', 
                'RECEIVED BY', 
                'ISSUE BY', 
                'LAST UPDATED'])
            instance = queryset
            for stock in instance:
                writer.writerow(
                [stock.category, 
                stock.item_name, 
                stock.quantity, 
                stock.issue_quantity, 
                stock.received_quantity, 
                stock.received_by, 
                stock.issue_by, 
                stock.last_updated])
            return response

        context = {
        "form": form,
        "header": header,
        "queryset": queryset,
    }
    return render(request, "list_history.html",context)

@login_required
def add_category(request):
    form = CategoryCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully Created')
        return redirect('/add_items')
    context = {
        "form": form,
        "title": "Add Category",
    }
    return render(request, "add_category.html", context)