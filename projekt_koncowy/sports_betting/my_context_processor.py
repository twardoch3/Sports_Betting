import datetime
def my_cp(request):
    ctx = {

    'today': datetime.date.today()
    }

    return ctx