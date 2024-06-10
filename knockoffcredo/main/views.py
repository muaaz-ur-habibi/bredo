from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

import requests as req
from bs4 import BeautifulSoup as bs

views = Blueprint("views", __name__)



#@views.route('/')
#@login_required
#def home():
#    return "<h1>HOME sweet HOME</h1>"

online_users = []


@views.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        id = request.form.get("idInput")
        pas = request.form.get("passwordInput")

        online_users.append({"USER": str(id), "PASS": str(pas)})

        id = str(id)
        pas = str(pas)

        print(id, pas)

        data = {
            "usr" : id,
            "pas" : pas,
            "log" : ""
        }

        with req.Session() as sesh:
            try:
                g = sesh.post("http://schoolportal.credo.edu.pk/schoolportal/loginn.php", data=data)
            except req.exceptions.ConnectionError:
                flash("Connection Error. Try again later", category="error")
                return render_template("signin.html")


            s = bs(g.content, "html.parser")
            c = s.find('section', {'class': 'content-header'})
            ch = c.findChild('h1')

            if 'Dashboard' in ch.text:
                print('yup, this shi works')
    
            try:
                if "Dashboard" in ch.text:
                        
                        online_users.append(id)
                        
                        #to scrape the student info
                        img = s.find('img', {'style': 'box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);;padding: 2px; border-radius: 8px;'}).attrs['src']
                        info = s.find_all("b")
                        more_info = s.find_all("div", {"class": "input-group"})


                        #to scrape the subjects
                        t = s.find("div", {"class": "col-lg-6 table-responsive"})
                        subs = t.findChildren("td")
                        subs = subs[3:]
                        print(subs)


                        #to scrape the fees
                        fee_data = {
                            "std_id_ledger" : id,
                            "fee_challan_fetch" : "Fee Ledger"
                        }
                                        
                        n_g = sesh.post("http://schoolportal.credo.edu.pk/schoolportal/pages/fee_challan/ajax/student_legder_output.php", data=fee_data)

                        n_s = bs(n_g.content, "html.parser")

                        m_table = n_s.find("table", {"class": "table table-bordered"})
                        m_table.findChildren("tr")
                        


                        useful_info = []

                        useful_info.append(info[3].text)
                        useful_info.append(info[4].text)
                        for i in more_info:
                            useful_info.append(i.text)
                        
                        subs = [str(i.text).strip() for i in subs]
                        print(subs)
                        subs = '|'.join(subs)
                        subs = subs.replace('\n', '')
                        #print(subs)
                        
                        #useful_info.append(subs)
                        
                        for i in m_table:
                            useful_info.append(i.text)

                        data_to_send = "|".join(useful_info)

                        #data_to_send.join(subs)
                        data_to_send = f'{data_to_send}|{subs}'
                        data_to_send = data_to_send.replace('\n', '')

                        #data_to_send.join(str(id))
                        #sesh.close()

                        return redirect(url_for("views.dashboard", useful_info=data_to_send, id=str(id), subjects=subs))
                else:
                    flash("Credentials are'nt valid. Try again", category="error")
                    return render_template("signin.html")
            except AttributeError:
                flash("Original portal is probably down. Try again later", category="error")
                return render_template("signin.html")
            except req.exceptions.ConnectionError:
                flash("Connection Error. Try again later", category="error")
                return render_template("signin.html")


    elif request.method == "GET":
        return render_template("signin.html")



@views.route("/dashboard")
def dashboard():
    incoming_data = request.args.get('useful_info')
    subjects = request.args.get('subjects')

    subjects = str(subjects).split('|')
    t_subs = []
    
    l = int(len(subjects)/3)
    
    i = 0
    x=0

    for s in range(l):
        t_a = []
        t_a.append(subjects[i])
        t_a.append(subjects[i+1])
        t_a.append(subjects[i+2])
        t_a.append(x)

        t_subs.append(t_a)
        x+=1
        i+=3
    
    print(t_subs)

    incoming_data = str(incoming_data)
    incoming_data = incoming_data.split("|")


    ID = request.args.get('id')

    if ID not in online_users:
        flash('You arent signed in', category='error')
        return redirect(url_for("views.signin"))

    incoming_data[1] = incoming_data[1].split(': ')[1]
    incoming_data[2] = 'Sigma' if incoming_data[2].split(": ")[1].strip() == 'Male' else 'House Object'
    incoming_data[3] = incoming_data[3].split(': ')[1]
    incoming_data[4] = incoming_data[4].split(':')[1]
    incoming_data[5] = incoming_data[5].split(':')[1]

    section = incoming_data[-2].split(' ')
    for i in section:
        if i.upper() in ['A', 'B', 'C', 'D', 'E']:
            section = i
        
    incoming_data[1] = incoming_data[1].replace('th', section).replace('Grade', '')

    incoming_data[6] = incoming_data[6].split(':')[1]
    incoming_data[7] = incoming_data[7].split(':')[1]
    incoming_data[8] = incoming_data[8].split(':')[1]
    incoming_data[8] = incoming_data[8] if incoming_data[8] != '' else '--'

    incoming_data[9] = incoming_data[9].split(':')[1]
    incoming_data[10] = incoming_data[10].split(':')[1]
    incoming_data[11] = incoming_data[11].split(':')[1]
    incoming_data[11] = incoming_data[11] if incoming_data[11] != '' else '--'

    incoming_data[12] = incoming_data[12].split(':')[1]
    incoming_data[13] = incoming_data[13].split(':')[1]
    incoming_data[14] = incoming_data[14].split(':')[1]
    
    return render_template("dashboard.html", data=incoming_data, subs=t_subs)


@views.route('/signout')
def signout():

    return '<h1>signout'