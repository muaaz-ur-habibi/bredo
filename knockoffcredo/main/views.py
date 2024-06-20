from flask import Blueprint, render_template, request, flash, redirect, url_for

import requests as req
from bs4 import BeautifulSoup as bs

views = Blueprint("views", __name__)


# declare a list that will store all the online users
online_users = []

# main signin page
@views.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # parameteres for the post request
        id = request.form.get("idInput")
        pas = request.form.get("passwordInput")

        online_users.append({"USER": str(id), "PASS": str(pas)})

        id = str(id)
        pas = str(pas)

        print(id, pas)

        # data for the post request
        data = {
            "usr" : id,
            "pas" : pas,
            "log" : ""
        }

        # initiate a session. this will also scrape all the necessary info from the school's dashboard
        with req.Session() as sesh:
            try:
                g = sesh.post("http://schoolportal.credo.edu.pk/schoolportal/loginn.php", data=data)
            except req.exceptions.ConnectionError:
                flash("Connection Error. Try again later", category="error")
                return render_template("signin.html")


            s = bs(g.content, "html.parser")
            c = s.find('section', {'class': 'content-header'})
            
            
            try:
                # check if the credentials are valid since this shows up if they are
                ch = s.find('h1')
                if ch is not None:                                
                        #to scrape the student info
                        img = s.find('img', {'style': 'box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);;padding: 2px; border-radius: 8px;'}).attrs['src']
                        info = s.find_all("b")
                        more_info = s.find_all("div", {"class": "input-group"})


                        #to scrape the subjects
                        t = s.find("div", {"class": "col-lg-6 table-responsive"})
                        subs = t.findChildren("td")
                        subs = subs[3:]


                        # to scrape the fees
                        fee_data = {
                            "std_id_ledger" : id,
                            "fee_challan_fetch" : "Fee Ledger"
                        }
                                        
                        n_g = sesh.post("http://schoolportal.credo.edu.pk/schoolportal/pages/fee_challan/ajax/student_legder_output.php", data=fee_data)

                        n_s = bs(n_g.content, "html.parser")

                        m_table = n_s.find("table", {"class": "table table-bordered"})
                        m = m_table.findChildren("tr")
                        m = [str(i.text).replace('\n', '') for i in m]
                        m = [x.replace(' - ', '-') for x in m]
                        
                        
                        # to scrape grades
                        g_g = sesh.get('http://schoolportal.credo.edu.pk/schoolportal/pages/exam_tab/exam_student.php')
                        g_s = bs(g_g.content, 'html.parser')
                        container_for_butts = g_s.find('div', {"class" : "col-lg-12 text-center table-responsive"})
                        c = container_for_butts.findChildren('input', {'type': 'button'})
                        number_of_grades = len(c)
                        grades_data = []
                        grades_data.clear()

                        for i in range(number_of_grades):
                            d = {
                                "e_n" : g_s.find('input', {'type': 'hidden', 'id': f'exam_name{i}'}).attrs['value'],
                                "e_no" : g_s.find('input', {'type': 'hidden', 'id': f'exam_number{i}'}).attrs['value'],
                                "t_w" : g_s.find('input', {'type': 'hidden', 'id': f'term_wise{i}'}).attrs['value'],
                                "y" : g_s.find('input', {'type': 'hidden', 'id': f'yearr{i}'}).attrs['value']
                            }

                            grades_data.append(d)

                        f_grades = []
                        
                        for i in grades_data:
                            grades_payload = {
                                "exam_name" : i['e_n'],
                                "exam_number" : i['e_no'],
                                "term_wise" : i['t_w'],
                                "yearr" : i['y'],
                                "std_id" : id
                            }

                            g_p = sesh.post('http://schoolportal.credo.edu.pk/schoolportal/pages/exam_tab/ajax/fetch_result.php', data=grades_payload)

                            g_p_s = bs(g_p.content, 'html.parser')
                            n = g_p_s.find('table', {'style': " border: 2px solid;font-size:16px;border-color:#999"})
                            grades = n.findChildren('tr')
                            grades = [t.text for t in grades]
                            grades.append([i['e_n'], i['y']])
                            f_grades.append(grades)
                        

                        grades_send = [j for i in f_grades for j in i]
                        f_grades_send = []
                        for i in grades_send:
                            if 'Subjects' not in i:
                                #print(f'> {i}')
                                try:
                                    i = str(i).replace(']', '').replace('[', '').replace("'", '')
                                except:
                                    pass
                                f_grades_send.append(i.strip())

                        # to scrape the attendence
                        first_date = list(id)[0:4]
                        first_date = ''.join(first_date)

                        attendence_payload= {
                            'id': id,
                            'first': f'{first_date}-08-01',
                            'last': f'{str(int(first_date)+1)}-06-01',
                            'sel': 'Student'
                        }

                        a_r = sesh.post("http://schoolportal.credo.edu.pk/schoolportal/pages/attendance/ajax/monthly_report.php", data=attendence_payload)
                        a_s = bs(a_r.content, features='html.parser')

                        t = a_s.find("table", {'class': 'table-hover table table-bordered'})
                        attendences = t.findChildren('td')
                        attendences = [f"{str(i.text)}" for i in attendences]

                        attendences = attendences[5:]
                        
                        attendences = '|'.join(i for i in attendences)

                        # convert the grades list to a string to send as a url parameter
                        f_grades_send = '|'.join(str(i).strip() for i in f_grades_send)

                        #convert the fees list into a string as well
                        fees_send = '|'.join(str(i) for i in m)

                        # define the list that will store the information to be sent
                        useful_info = []

                        # appending all the useful info to the list to be sent
                        useful_info.append(info[3].text)
                        useful_info.append(info[4].text)
                        for i in more_info:
                            useful_info.append(i.text)
                        
                        # create a seperate list for subjects
                        subs = [str(i.text).strip() for i in subs]

                        subs = '|'.join(subs)
                        subs = subs.replace('\n', '')

                        # append the fee info to the list to be sent
                        for i in m_table:
                            useful_info.append(i.text)

                        # convert the list to be sent into a string with a seperation criteria since this is a web url parameter
                        data_to_send = "|".join(useful_info)

                        # append the subjects to this
                        data_to_send = f'{data_to_send}|{subs}'
                        data_to_send = data_to_send.replace('\n', '')

                        # append the current id to the list of users that are online
                        online_users.append(str(id))

                        # finally redirect the user to the primary dashboard page with all the necessary info as parameters
                        return redirect(url_for("views.dashboard", useful_info=data_to_send, id=str(id), subjects=subs, grades=f_grades_send, fees=fees_send, attendence=attendences, whereto='personal'))
                else:
                    # if the check failed means the credentials werent valid
                    flash("Credentials aint valid", category="error")
                    return render_template("signin.html")
            # but if a connection error occured ask user to try again
            except req.exceptions.ConnectionError:
                flash("Connection Error. Try again later", category="error")
                return render_template("signin.html")


    elif request.method == "GET":
        return render_template("signin.html")


# whereto specifies where the data should be sent to. main is the personal info page
@views.route("/dashboard/<string:whereto>")
def dashboard(whereto):
    # declare all the incoming data as variables
    incoming_data_o = request.args.get('useful_info')
    subjects_o = request.args.get('subjects')
    grades = request.args.get('grades')
    fees = request.args.get('fees')
    attendences = request.args.get('attendence')


    attendences_o = attendences
    fees_o = fees
    grades_o = grades

    # split based on the criteria specified above
    subjects = str(subjects_o).split('|')
    t_subs = []
    
    l = int(len(subjects)/3)
    
    i = 0
    x=0

    # just seperate and clean all the data
    for s in range(l):
        t_a = []
        t_a.append(subjects[i])
        t_a.append(subjects[i+1])
        t_a.append(subjects[i+2])
        t_a.append(x)

        t_subs.append(t_a)
        x+=1
        i+=3
    

    incoming_data = str(incoming_data_o)
    incoming_data = incoming_data.split("|")


    ID = request.args.get('id')

    # if user tried to go to dashboard without signing in throw an error
    if ID not in online_users:
        flash('You arent signed in', category='error')
        return redirect(url_for("views.signin"))
    
    # prettifying the main data
    incoming_data[1] = incoming_data[1].split(': ')[1]
    incoming_data[2] = 'Male' if incoming_data[2].split(": ")[1].strip() == 'Male' else 'Female'
    incoming_data[3] = incoming_data[3].split(': ')[1]
    incoming_data[4] = incoming_data[4].split(':')[1]
    incoming_data[5] = incoming_data[5].split(':')[1]

    section = incoming_data[-2].split(' ')
    for i in section:
        if i.upper() in ['A', 'B', 'C', 'D', 'E']:# although my school only has 3 grades but oh well just to be safe
            section = i
        else:
            section = "ALIEN"
        
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

    # prettifying the grades data
    grades_to_send = []

    grades = grades.split("|")

    for i in grades:
        temp_send = []
        if ',' in i:
            temp_send.append(i)
            pass
        #print(i)

        i = i.split("   ")
        try:
            teacher_and_subject = i[0].split("  ")
            if len(teacher_and_subject) < 3:
                temp_send.append(teacher_and_subject[0])
                temp_send.append(teacher_and_subject[1])
            elif len(teacher_and_subject) > 2:
                teacher_and_subject[1] = teacher_and_subject[1] + teacher_and_subject[2]
                temp_send.append(teacher_and_subject[0])
                temp_send.append(teacher_and_subject[1])
        except:
            pass
        
        try:
            if i[1].strip() != 'ABSENT':
                max_min_percent_grade = i[1].split('  ')
                max_marks = max_min_percent_grade[0]
                max_min_percent_grade = max_min_percent_grade[1].split(' ')
                min_marks = max_min_percent_grade[0]
                percent = max_min_percent_grade[1]
                grade = max_min_percent_grade[2]
            
                temp_send.append(max_marks)
                temp_send.append(min_marks)
                temp_send.append(percent)
                temp_send.append(grade)
            else:
                temp_send.append("ABSENT")
                temp_send.append("ABSENT")
                temp_send.append("ABSENT")
                temp_send.append("ABSENT")
        except:
            pass
        
        if len(temp_send) == 2:
            temp_send = temp_send[0]
        grades_to_send.append(temp_send)

    final_g_to_send = []

    # prettifying the subjects data
    while grades_to_send:
        sub = []

        while grades_to_send:
            it = grades_to_send.pop(0)

            if isinstance(it, list):
                sub.append(it)
            else:
                sub.append(it)
                break

        final_g_to_send.append(sub)

    # prettifying the fees data
    fees = fees.split("|")
    fees = fees[1:]
    fees_to_send = []
    for i in fees:
        i = i.strip().split(" ")
        fees_to_send.append(i)

    # prettifying the attendences data
    attendences = attendences.split('|')
    
    attendences_to_send = []
    for i in range(0, len(attendences), 5):
        x = [attendences[i], attendences[i+1], attendences[i+3], attendences[i+4]]
        
        attendences_to_send.append(x)

    # check where does the user want to go and send them there with all the data. this way the user can keep using the site even if their internet gets disconnected
    if whereto == 'personal':
        return render_template("dashboard.html", data=incoming_data, subs=t_subs, id=ID, original_subs=subjects_o, original_data=incoming_data_o, grades_s=final_g_to_send, original_grades=grades_o, fees_s=fees_to_send, original_fees=fees_o, attendence_s=attendences_to_send, original_attendence=attendences_o)
    elif whereto == 'grades':
        return render_template("grades.html", data=incoming_data, subs=t_subs, id=ID, original_subs=subjects_o, original_data=incoming_data_o, grades_s=final_g_to_send, original_grades=grades_o, fees_s=fees_to_send, original_fees=fees_o, attendence_s=attendences_to_send, original_attendence=attendences_o)
    # school's attendance getting function is seriously messed up man. still alot of working to do on this
    elif whereto == 'attendance':
        return render_template("attendance.html", data=incoming_data, subs=t_subs, id=ID, original_subs=subjects_o, original_data=incoming_data_o, grades_s=final_g_to_send, original_grades=grades_o, fees_s=fees_to_send, original_fees=fees_o, attendence_s=attendences_to_send, original_attendence=attendences_o)
    elif whereto == 'fee':
        return render_template("fees.html", data=incoming_data, subs=t_subs, id=ID, original_subs=subjects_o, original_data=incoming_data_o, grades_s=final_g_to_send, original_grades=grades_o, fees_s=fees_to_send, original_fees=fees_o, attendence_s=attendences_to_send, original_attendence=attendences_o)