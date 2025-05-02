from django.shortcuts import render, redirect

def authenticated(view_func):
  def is_authenticated(request, *args, **kwargs):

    if request.user.is_authenticated:
      return redirect('Home')
    else:
      return view_func(request, *args, **kwargs)
    
  return is_authenticated