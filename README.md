site is live!: check it out: https://bredo.koyeb.app/
Disclaimer: due to security and privacy reasons outsiders cannot view this site.
<br>
<h1 align="center"><center>BREDO! The Better Credo (website)</center></h1>
<h4 align="center">Developed by a self-taught Python Dev student of Credo School</h4>
<h3>Soo, what and why? Well:</h3>
<ul>
  <li>Our original School website is really bland</li>
  <li>Also, its quite difficult to navigate huh.</li>
  <li>UI is questionable.</li>
  <li>So, i decided to take matters into my own hands and test my own web dev skills.</li>
  <li>NGL, this was actually quite fun to make.</li>
  <li>Most importanty: This is made by a student. Come on now, which student has made a better school website for their school huh?</li>
</ul>
<hr>
<h4>Frameworks and languages used to make this:</h4>
<ul>
  <li>Python</li>
  <li>Flask - Python</li>
  <li>Requests - Python</li>
  <li>BeautifulSoup4 - Python</li>
  <li>HTML</li>
  <li>Bootstrap CSS</li>
  <li>Javascript</li>
</ul>
<hr>
<h3>How does all the stuff in views.py work? (that's the main program)</h3>
<p>
  A basic and surface level run-down, the signin route uses Python Requests to get the user credentials that they insert to send a post request to the school's login page, once logged in it uses a session to stay connected, then it scrapes all the necessary data using BeautifulSoup4, and all the data that IS scrapable, sends it to the main dashboard route, where the data is refined, processed and cleaned, then sends to the HTML templates which use Jinja to display the data. CSS is used to beutify the page. So far Javascript is only used in the login page. The main back-end is built with only Flask. For better explanation i have added comments.
</p>
<hr>
<h4>By the way here's a roadmap. I wanna add all this into this amazing website (EVERYTHING IS UP AND RUNNING)</h4>
<p>❌ means not started. 🚧 means working on it. ✅ means up and running. ⏳ means i give up on this for now</p>
<ul>
  <li>Nice UI  ✅</li>  
  <li>Show basic student info  ✅</li>  
  <li>Show student faculty and subjects info  ✅</li>  
  <li>Show student exam reports  ✅</li>  
  <li>Show student attendence info  ✅</li>
  <li>Show student fees info ✅</li>
</ul>
<br>
If youve got anything that you think should be here let me know.
Thank you for reading.
