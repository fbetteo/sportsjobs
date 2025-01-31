
## MANUALLY POST JOB VIA API


from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime, timezone
import json

# EDIT HTML IN INSPECT AND PASTE HERE
html_content = """<div class="mx-auto max-w-[750px] prose font-company-body overflow-hidden break-words [&amp;_ol_li_li]:list-[lower-alpha]" data-controller="careersite--responsive-video">
    <h3><strong>The Role</strong></h3><hr><p>We are looking for a self-driven, talented <strong>Research Engineer</strong> who will take AI / deep learning projects from conception to delivery, collaborating with colleagues to keep our club at the forefront of applied football analytics research and competing for trophies with a distinct, data-driven advantage.&nbsp;</p><p>Your work will impact our club across the competitive footballing spectrum including performance and recruitment, whether that be helping our Women's and Men’s First Team coaches prepare for an upcoming match or helping our player recruitment specialists identify outstanding upcoming talent.&nbsp;<br> <br>You will apply your knowledge of state-of-the-art deep learning techniques (e.g. Transformers, Diffusion, Reinforcement Learning and Geometric Deep Learning) to a variety of football-derived data, train and deploy bespoke models and you'll collaborate with software engineers, UX designers and football analysts to build applications leveraging those models. Data will span multiple modes (spatiotemporal, image/video, text, tabular/numeric) and present intriguing engineering challenges for scalability and performance.</p><p>&nbsp;</p><h3><strong>Who we are</strong></h3><hr><p>We are one of the most famous clubs in world football, with a rich heritage and history of success – read more about our history, <a href="https://www.arsenal.com/history">here</a>.  </p><p>Beyond that, we are passionate about our <a href="https://www.arsenal.com/community">local community</a> and, behind the scenes, we have a wide variety of opportunities and career paths for all. We have a very defined purpose: to act for a winning team, culture and community. We achieve this by ensuring we are courageous in the pursuit of progress, we champion our community and each other, and that we do the right thing (even when no one is looking).<br></p><h3><br></h3><h3>
<strong>Your day-to-day</strong><br>
</h3><hr><ul>
<li>
<strong>Design, develop and deploy bespoke AI models</strong>&nbsp;- you’ll be a subject matter expert in deep learning and generative AI, contributing cutting-edge knowledge to projects&nbsp;</li>
<li> <strong>Conduct applied AI research</strong>&nbsp;- you will be entrusted to&nbsp;address complex, unsolved challenges, particularly in modelling and analysing spatiotemporal and multimodal datasets</li>
<li>
<strong>Collaborate with colleagues</strong>&nbsp;- you’ll partner with&nbsp;with coaches, analysts, scouts and technical peers to tackle difficult problems and provide users with applicable solutions, whether that be identifying the right loan placement for breakthrough academy players or the ideal ball trajectory for free kicks&nbsp;</li>
<li>
<strong>Embrace the entire stack</strong>&nbsp;- you’ll collaborate with a small, multidisciplinary team where everybody is willing to roll up their sleeves and dive into unfamiliar territory, whether it be hacking together an interactive tactics board in ReactJS or plumbing model inference into a PySpark data pipeline&nbsp;</li>
<li>
<strong>Communicate key insights</strong>&nbsp;- you will make data-driven recommendations to a variety of audiences, including technical teams and non-technical stakeholders, ensuring clarity and engagement&nbsp;</li>
<li>
<strong>Keep abreast of industry trends </strong>-&nbsp;you'll enthusiastically be&nbsp;part of the greater AI community, sharing recent developments with peers and advocating for adoption of new technologies and methods where warranted&nbsp;</li>
<li>
<strong>Be part of a geo-distributed team </strong>- you will relish the opportunity to unite with colleagues in other global locations and efficiently manage the dynamics of collaborating with team members in&nbsp;different timezones</li>
<li>
<strong>Mentor </strong><strong>and learn </strong>-&nbsp;you'll proudly mentor peers and eagerly learn from others, whether that be from colleagues across our club or at meetups and conferences with fellow industry experts</li>
</ul><h3></h3><h3></h3><p>&nbsp;</p><h3>
<strong>What we are looking for</strong><br>
</h3><hr><ul>
<li>
<strong>Proven quantitative background </strong>-&nbsp;you hold an advanced qualification in a quantitative discipline (e.g., computer science, artificial intelligence, mathematics, statistics, data visualisation,  data science), or a related field with proven expertise in modern ML/AI methodologies&nbsp;</li>
<li>
<strong>Understanding of programming fundamentals </strong>-&nbsp;you have a solid foundation in software engineering and machine learning principles&nbsp;</li>
<li>
<strong>Applied deep learning experience </strong>- you're well versed in applying deep learning to unique and complex challenges and you have a track record of engineering end-to-end solutions that leverage deep learning models&nbsp;</li>
<li>
<strong>Excellent written and verbal communication </strong>-&nbsp;you can communicate confidently and effectively with both technical and non-technical stakeholders, whether they are standing in the room with you or asynchronously exchanging messages across time zones&nbsp;</li>
<li>
<strong>Highly independent and self-motivated mindset</strong>&nbsp;- you thrive when you need to take the torch and carry it on your own, calling for self-discipline, proactive communication and a manager-of-one mentality&nbsp;</li>
<li>
<strong>Innately curious and an&nbsp;independent learner </strong>-&nbsp;you naturally let your curiosity and passion for crafting new solutions guide you in acquiring new skills and becoming competent in a new discipline gives you great satisfaction&nbsp;</li>
<li>
<strong>PyData</strong><strong> tech stack fluency</strong>&nbsp;- you are comfortable with Python, numpy, Pandas/Polars and similar tech</li>
<li>
<strong>Experience with deep learning frameworks </strong>-&nbsp;you have worked with PyTorch, JAX, Keras and/or TensorFlow </li>
</ul><h2></h2><h3><br></h3><h3><strong>Why choose us <br></strong></h3><hr><p>At Arsenal, we want everyone to feel a sense of trust and belonging, so we are proud of both our club values and also what we offer to our employees. As one of our Gunners, you will receive:</p><ul>
<li>An exciting reward and recognition scheme</li>
<li>Generous holiday allowance which increases with your length of service</li>
<li>Great internal learning and development programmes</li>
<li>A flexible hybrid working model</li>
<li><span dir="ltr">Priority access to apply for match tickets</span></li>
<li>A competitive health and wellbeing benefits package</li>
<li>A leading Employee Assistance Programme</li>
<li>Great discounts with some of our Partners</li>
</ul><h3></h3><h3><br></h3><h3><strong>Arsenal for Everyone<br></strong></h3><hr><p>Arsenal for Everyone is our commitment to promoting and embracing equality, diversity and inclusion, so that everyone connected to the club feels like they belong to the same Arsenal family. We believe that diversity of background, skills and experience drives our success on and off the pitch. </p><h3><br></h3><h3>
<strong>Disability Confident Leader</strong><br>
</h3><hr><p>We are a Disability Confident Leader. We actively welcome and encourage applications from people with disabilities and long-term health conditions. If you need disability-related adjustments to the recruitment process, please indicate this in your application.</p><p>If you are likely to meet the definition of being a ‘disabled person’ according to the <a href="https://www.gov.uk/guidance/equality-act-2010-guidance">Equality Act 2010</a>, you may be eligible to apply for an interview via the <a href="https://www.gov.uk/government/publications/disability-confident-guidance-for-levels-1-2-and-3/level-1-disability-confident-committed#offer-an-interview-to-disabled-people" target="_blank">Disability Confident Scheme</a> - please indicate this in your application form below. The information you share with us about your health or disability will not be used in recruitment decisions.</p><p><br></p><h3>Application Closing Date - Wednesday 5th February 2025</h3><hr><p></p><p>Please note: we reserve the right to close the position early if application volumes are particularly high. We encourage you to get your application in sooner rather than later. </p><p>Good luck! </p><p><br></p>
  </div>"""

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
# Extract the content inside the div IF NECESSARY
# description_div = soup.find('div', {'data-automation-id': 'jobPostingDescription'})

# Convert HTML to Markdown
if soup:
    markdown_description = md(str(soup))
    print(markdown_description)
else:
    print("Description not found.")

post_body = {
    "name": "Research Engineer",  # Job title or post name
    "url": "https://careers.arsenal.com/jobs/5434108-research-engineer",  # Link to the job or post
    "location": "Sobha Realty Training Centre, London",  # City or region
    "country": "united kingdom",  # Country
    "seniority": "With Experience",  # Level (e.g., Junior, Mid, Senior)
    "description": markdown_description,  # Detailed description of the job or post
    "sport_list": ['Football - Soccer'],  # Relevant sports categories, if any
    "skills": None,  # List of required skills (e.g., ["Python", "Data Analysis"])
    "remote_office": "Office",  # Whether it's remote, office, or hybrid
    "salary": "-",  # Salary information (e.g., "50k-70k USD per year")
    "language": ["English"],  # List of required languages (e.g., ["English", "Spanish"])
    "company": "Arsenal FC",  # Company name
    "industry": "Sports",  # Industry type (e.g., "Sports Analytics")
    "hours": "Fulltime",  # Working hours (e.g., "Full-time", "Part-time")
    "featured": "1 - regular",  # Regular by default
    "logo_permanent_url": "https://images.teamtailor-cdn.com/images/s3/teamtailor-production/logotype-v3/image_uploads/006048fc-5a6e-49be-8a75-23c87bade87d/original.png",  # Default logo
    "creation_date": str(datetime.now(timezone.utc)),  # Automatically set creation date
}



aa = json.dumps(post_body, ensure_ascii=False)

print(aa)


# PASTE THE PRINT IN https://jsonlint.com/ AND COPY THE RESULT BELOW#
{
    "name": "Research Engineer",
    "url": "https://careers.arsenal.com/jobs/5434108-research-engineer",
    "location": "Sobha Realty Training Centre, London",
    "country": "united kingdom",
    "seniority": "With Experience",
    "description": "\n### **The Role**\n\n\n\n---\n\nWe are looking for a self\\-driven, talented **Research Engineer** who will take AI / deep learning projects from conception to delivery, collaborating with colleagues to keep our club at the forefront of applied football analytics research and competing for trophies with a distinct, data\\-driven advantage. \n\nYour work will impact our club across the competitive footballing spectrum including performance and recruitment, whether that be helping our Women's and Men’s First Team coaches prepare for an upcoming match or helping our player recruitment specialists identify outstanding upcoming talent.   \n   \nYou will apply your knowledge of state\\-of\\-the\\-art deep learning techniques (e.g. Transformers, Diffusion, Reinforcement Learning and Geometric Deep Learning) to a variety of football\\-derived data, train and deploy bespoke models and you'll collaborate with software engineers, UX designers and football analysts to build applications leveraging those models. Data will span multiple modes (spatiotemporal, image/video, text, tabular/numeric) and present intriguing engineering challenges for scalability and performance.\n\n \n\n### **Who we are**\n\n\n\n---\n\nWe are one of the most famous clubs in world football, with a rich heritage and history of success – read more about our history, [here](https://www.arsenal.com/history). \n\nBeyond that, we are passionate about our [local community](https://www.arsenal.com/community) and, behind the scenes, we have a wide variety of opportunities and career paths for all. We have a very defined purpose: to act for a winning team, culture and community. We achieve this by ensuring we are courageous in the pursuit of progress, we champion our community and each other, and that we do the right thing (even when no one is looking).  \n\n\n### \n\n### **Your day\\-to\\-day**\n\n\n\n---\n\n* **Design, develop and deploy bespoke AI models** \\- you’ll be a subject matter expert in deep learning and generative AI, contributing cutting\\-edge knowledge to projects\n* **Conduct applied AI research** \\- you will be entrusted to address complex, unsolved challenges, particularly in modelling and analysing spatiotemporal and multimodal datasets\n* **Collaborate with colleagues** \\- you’ll partner with with coaches, analysts, scouts and technical peers to tackle difficult problems and provide users with applicable solutions, whether that be identifying the right loan placement for breakthrough academy players or the ideal ball trajectory for free kicks\n* **Embrace the entire stack** \\- you’ll collaborate with a small, multidisciplinary team where everybody is willing to roll up their sleeves and dive into unfamiliar territory, whether it be hacking together an interactive tactics board in ReactJS or plumbing model inference into a PySpark data pipeline\n* **Communicate key insights** \\- you will make data\\-driven recommendations to a variety of audiences, including technical teams and non\\-technical stakeholders, ensuring clarity and engagement\n* **Keep abreast of industry trends** \\- you'll enthusiastically be part of the greater AI community, sharing recent developments with peers and advocating for adoption of new technologies and methods where warranted\n* **Be part of a geo\\-distributed team** \\- you will relish the opportunity to unite with colleagues in other global locations and efficiently manage the dynamics of collaborating with team members in different timezones\n* **Mentor** **and learn** \\- you'll proudly mentor peers and eagerly learn from others, whether that be from colleagues across our club or at meetups and conferences with fellow industry experts\n\n### \n\n### \n\n \n\n### **What we are looking for**\n\n\n\n---\n\n* **Proven quantitative background** \\- you hold an advanced qualification in a quantitative discipline (e.g., computer science, artificial intelligence, mathematics, statistics, data visualisation, data science), or a related field with proven expertise in modern ML/AI methodologies\n* **Understanding of programming fundamentals** \\- you have a solid foundation in software engineering and machine learning principles\n* **Applied deep learning experience** \\- you're well versed in applying deep learning to unique and complex challenges and you have a track record of engineering end\\-to\\-end solutions that leverage deep learning models\n* **Excellent written and verbal communication** \\- you can communicate confidently and effectively with both technical and non\\-technical stakeholders, whether they are standing in the room with you or asynchronously exchanging messages across time zones\n* **Highly independent and self\\-motivated mindset** \\- you thrive when you need to take the torch and carry it on your own, calling for self\\-discipline, proactive communication and a manager\\-of\\-one mentality\n* **Innately curious and an independent learner** \\- you naturally let your curiosity and passion for crafting new solutions guide you in acquiring new skills and becoming competent in a new discipline gives you great satisfaction\n* **PyData** **tech stack fluency** \\- you are comfortable with Python, numpy, Pandas/Polars and similar tech\n* **Experience with deep learning frameworks** \\- you have worked with PyTorch, JAX, Keras and/or TensorFlow\n\n### \n\n### **Why choose us**\n\n\n\n---\n\nAt Arsenal, we want everyone to feel a sense of trust and belonging, so we are proud of both our club values and also what we offer to our employees. As one of our Gunners, you will receive:\n\n* An exciting reward and recognition scheme\n* Generous holiday allowance which increases with your length of service\n* Great internal learning and development programmes\n* A flexible hybrid working model\n* Priority access to apply for match tickets\n* A competitive health and wellbeing benefits package\n* A leading Employee Assistance Programme\n* Great discounts with some of our Partners\n\n### \n\n### \n\n### **Arsenal for Everyone**\n\n\n\n---\n\nArsenal for Everyone is our commitment to promoting and embracing equality, diversity and inclusion, so that everyone connected to the club feels like they belong to the same Arsenal family. We believe that diversity of background, skills and experience drives our success on and off the pitch. \n\n### \n\n### **Disability Confident Leader**\n\n\n\n---\n\nWe are a Disability Confident Leader. We actively welcome and encourage applications from people with disabilities and long\\-term health conditions. If you need disability\\-related adjustments to the recruitment process, please indicate this in your application.\n\nIf you are likely to meet the definition of being a ‘disabled person’ according to the [Equality Act 2010](https://www.gov.uk/guidance/equality-act-2010-guidance), you may be eligible to apply for an interview via the [Disability Confident Scheme](https://www.gov.uk/government/publications/disability-confident-guidance-for-levels-1-2-and-3/level-1-disability-confident-committed#offer-an-interview-to-disabled-people) \\- please indicate this in your application form below. The information you share with us about your health or disability will not be used in recruitment decisions.\n\n  \n\n\n### Application Closing Date \\- Wednesday 5th February 2025\n\n\n\n---\n\nPlease note: we reserve the right to close the position early if application volumes are particularly high. We encourage you to get your application in sooner rather than later. \n\nGood luck! \n\n  \n\n\n\n",
    "sport_list":
        "Football - Soccer"
    ,
    "skills": null,
    "remote_office": "Office",
    "salary": "-",
    "language": [
        "English"
    ],
    "company": "Arsenal FC",
    "industry": "Sports",
    "hours": "Fulltime",
    "featured": "1 - regular",
    "logo_permanent_url": "https://images.teamtailor-cdn.com/images/s3/teamtailor-production/logotype-v3/image_uploads/006048fc-5a6e-49be-8a75-23c87bade87d/original.png",
    "creation_date": "2025-01-26 17:59:17.623435+00:00"
}

# GO TO REQBIN AND POST THE JSON TO THE API