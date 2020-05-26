from datetime import datetime


def multi_replace(s, old, new):
    """
    批量替换
    """
    assert len(old) == len(new)
    s = s.lower()
    for i in range(len(old)):
        s = s.replace(old[i].lower(), new[i])
    return s


def str_to_date(date_str, country='US'):
    """
    将字符串转化为标准时间
    """
    assert country in ['US', 'DE', 'FR', 'JP', 'MX', 'IN', 'CA', 'ES', 'UK', 'IT', 'AU']

    to_month = [u'January', u'February', u'March', u'April', u'May', u'June',
                u'July', u'August', u'September', u'October', u'November', u'December']

    if country in ['US', 'CA']:
        return datetime.strptime(date_str.strip(), '%B %d, %Y')

    elif country in ['UK', 'IN', "AU"]:
        try:
            return datetime.strptime(date_str.strip(), '%d %B %Y')
        except:
            return datetime.strptime(date_str.strip(), '%B %d, %Y')

    elif country == 'JP':
        date_str = date_str.replace(u'\u5e74', 'year').replace(u'\u6708', 'month').replace(u'\u65e5', 'day')
        return datetime.strptime(date_str.strip().encode('utf8'), '%Yyear%mmonth%dday')

    elif country == 'IT':
        from_month = [
            u'Gennaio', u'Febbraio', u'Marzo', u'Aprile', u'Maggio', u'Giugno',
            u'Luglio', u'Agosto', u'Settembre', u'Ottobre', u'Novembre', u'Dicembre'
        ]
        date_str = multi_replace(date_str, from_month, to_month)
        date_str = date_str.replace('il ', '')
        try:
            return datetime.strptime(date_str.strip(), '%d %B %Y')
        except ValueError:
            return datetime.strptime(date_str.strip(), '%d %b%Y')

    elif country == 'FR':
        from_month = [
            u'Janvier', u'Février', u'Mars', u'Avril', u'Mai', u'Juin',
            u'Juillet', u'Août', u'Septembre', u'Octobre', u'Novembre', u'Décembre'
        ]
        date_str = multi_replace(date_str, from_month, to_month)
        return datetime.strptime(date_str.strip(), '%d %B %Y')

    elif country in ['ES', 'MX']:
        from_month = [
            u'Enero', u'Febrero', u'Marzo', u'Abril', u'Mayo', u'Junio',
            u'Julio', u'Agosto', u'Septiembre', u'Octubre', u'Noviembre', u'Diciembre'
        ]
        date_str = multi_replace(date_str, from_month, to_month)
        date_str = date_str.replace('el ', '')
        return datetime.strptime(date_str.strip(), '%d de %B de %Y')

    elif country == 'DE':
        from_month = [
            u'Januar', u'Februar', u'März', u'April', u'Mai', u'Juni',
            u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'
        ]
        date_str = multi_replace(date_str, from_month, to_month)
        return datetime.strptime(date_str.strip(), '%d. %B %Y')
