---
layout: page
title: Personas
permalink: /personas/
parent: Design Documents
nav_order: 1
---

# Personas

If you have feedback, please [comment on personas](https://docs.google.com/forms/d/e/1FAIpQLSeZ3WLjaPdJWjPMYSc4BjTVIIv_fnHm7D1vKk1pqsx9tnNQsQ/viewform?usp=sf_link) by April 25th!

* [Nicholas Garza, Archivist](#nicholas-garza-archivist)
* [Emily Cooper, IT Professional](#emily-cooper-it-professional)
* [Andrea Lee, Digital Archivist](#andrea-lee-digital-archivist)
* [Teresa Burns, Historian](#teresa-burns-historian)
* [Isaac Hoffman, Data Scientist](#isaac-hoffman-data-scientist)
* [Aaron Santos, Tool Maintainer](#aaron-santos-tool-maintainer)
* [Gary Richardson, Self-Archivist](#gary-richardson-self-archivist)


## Nicholas Garza, Archivist 

<img src="../persona_images/nicholasGarza.jpg" alt="Image of Nicholas Garza." width="500px"/>


Nicholas Garza is a lone arranger at a small archive. He works mostly with books, paper documents and print-based photography, but is venturing into digital records since his archive is increasingly acquiring more of these records on optical media and external hard drives. He is comfortable moving files around and keeping multiple copies on external hard drives. He has gone to several sessions at conferences on how to preserve electronic records, and has been discussing email archives with colleagues at regional archives conferences and colleagues in online forums, but hasn’t had the opportunity to work with email yet. However, a recent conversation with a potential donor highlighted an email account containing valuable documentation, so he needs to find tools he can use to acquire, arrange, describe and preserve these records. Due to budgetary restrictions, he is limited to free tools he can find online.



Nicholas is partially sighted as the result of a medical condition. His preferred reading format is large print and he often increases the size of text when using a computer. He likes software that allows him to quickly change font size, backlight, and color schemes as his eyes fatigue and sometimes uses the NV Access screen reader when his eyes get tired.



#### Goals

- Nicholas wants to be able to easily and quickly export or convert email into a stable package so all the important content will still be there when he returns, potentially even years later.
- He wants a format for storing emails that he can easily duplicate and preserve on external hard drives or freemium cloud services.
- Nicholas wants to be able to easily view the email account to see what’s inside in order to describe the collection and discover any access issues.
- Nicholas also wants to provide easy access to certain emails or groups of emails to assist patrons and demonstrate their value.
- Nicholas wants software that makes it easy to increase font size or enables full use of a screen reader.

#### Pain Points

- Nicholas has more collections than he can manage well, so he’s always short on time.
- He has very limited technical assistance other than access to peer groups and what he can find online, so he’s likely to be frustrated by any errors unless the exact error message shows up prominently in search results or is a known issue in his professional community.
- The limited desktop support team at his archive is concerned that open source desktop tools might be malware.



#### Technology Use

Nicholas uses a Windows desktop computer provided by his archive. Although he is interested in learning about new tools, his ability to experiment is limited because he does not have administrator access to his computer, so cannot install any new software. He is comfortable learning and using a variety of web and desktop applications, but has no command line experience and wouldn't know where to start with a command-line only tool.



## Emily Cooper, IT Professional

<img src="../persona_images/emilyCooper.jpg" alt="Image of Emily Cooper." width="300px"/>


Emily Cooper is a technologist for a small organization that wishes to donate its records to an archival repository. She spends a lot of time doing desktop support across the organization while also managing a number of vendor services. She works in a Windows environment and doesn't officially support any Unix-like systems. Emily sometimes gets tasked with resolving general technical issues outside of her primary role. Her organization has donated records to an archival repository in the past, and recent discussions with the curators at the archive have shown the documentary value of her organization’s email. Overall, the organization has decided to take a “Capstone” approach to its email and focus on a few accounts used by the organization's leadership. They also do not wish to export entire accounts, but only include or exclude email folders. Emily has been charged with supporting this project from the IT side of the organization.

#### Goals

- Emily wants to export all of the relevant email accounts at once. Some accounts are available over IMAP, while older accounts were exported to PST files using an older version of Microsoft Outlook after the user retired.
- She sometimes wants to exclude specific email folders from transfer, and may sometimes wish to only include specific folders.
- After packaging, Emily would like to verify which folders and the numbers of email which were packaged.
- Once emails have been transferred to the archive, she would like some way that the archives can verify that the transfer completed so she can delete the original data and move on to the next project.

#### Pain points

- Emily is wary of tools that require multiple dependencies, which could potentially take a lot of time to set up, debug, and maintain.
- She can set an export to run overnight, but wants the process to complete in a reasonable amount of time, otherwise they suspect an issue.
- Emily often has trouble convincing administrators that open source tools without paid support are the best option.

#### Technology Use

Emily has a great deal of expertise and experience with technology. Although her organization is a Windows-only environment, she has some experience downloading and running Unix-focused open source tools on an ad hoc basis. She is comfortable administering a wide range of applications and infrastructure, but is not able to support all of the applications her organization uses, and relies on vendor support and software-as-a-service models.




## Andrea Lee, Digital Archivist

<img src="../persona_images/andreaLee.jpg" alt="Image of Andrea Lee." width="300px"/>



Andrea Lee is a new professional in a medium to large special collections department at a large university. Her position requires her to work across many functional boundaries to acquire, process, and provide access to electronic records. She also assists other archivists in working with technology, like preparing curators to discuss born-digital records with donors. Andrea enjoys the challenges of learning new technologies and applying them to her work, but is often frustrated by institutional barriers and interpersonal politics, which impede her ability to do her job effectively. Andrea’s city has a large Somalian community and her department is trialing an community archives program where they provide guidance to community groups in preserving their records. 



#### Goals

- Andrea would like to rapidly process email exports from donors and get them into a stable format.
- Andrea sometimes worries that electronic records may lose their integrity during transfer, so ideally she would prefer records to come packaged with checksums that she can verify them on receipt. However, most transfers use whatever methods the donor is most comfortable with, so she needs to be able to work with common export formats transferred using a variety of methods.
- Andrea heard about Mailbag from one of her colleagues at another institution, and would like to be able to use it as a Python library in her scripts to automate parts of processing email.
- Andrea knows that the Somalian community groups she is working with often use email announcements and is looking for a free tool that would enable them to preserve these records.

#### Pain points

- Andrea sometimes tries to teach donors how to use tools to package records prior to transfer and this can be challenging in many cases
- It can be challenging for Andrea to get support for web applications or tools that require servers and long term maintenance and support



#### Technology Use

Andrea specializes in learning and using a variety of open source tools. She is comfortable with the command line and sometimes uses Python scripting to automate processing and other repetitive tasks. She is also familiar with specialized hardware necessary for disk imaging and processing electronic records. Although she can install software on her Mac work laptop, she does not have easy access to server infrastructure for applications which require substantial processing power, or which need to be set up for ongoing use by multiple users.






## Teresa Burns, Historian

<img src="../persona_images/teresaBurns.jpg" alt="Image of Teresa Burns" width="500px"/>

Teresa Burns is a graduate student at a university working towards her doctorate focusing on the history of technology. She is aware of “Digital Humanities” approaches and has attended digital-focused sessions at a regional conference, but thus far has used traditional methods in her research. Teresa took a class on digital history where the final project was to build an Omeka-based web exhibit. Teresa would like to bolster the primary sources used in her dissertation with communications found in email archives.



#### Goals

- Teresa wants to browse by email listed sender, recipient, and date
- She is most comfortable viewing emails as PDF documents
- Teresa wants to view the full contents of emails along with any attachments
- She wants emails to include any metadata that might be relevant to its provenance



#### Pain points

- Teresa finds that each archive has their own unique systems and processes for providing access to electronic records. Learning how to use them can be frustrating and time consuming.
- In addition, she has a hard time finding email archives relevant to her research.



#### Technology Use

Teresa primarily uses her Mac laptop, which she takes with her whenever she travels to an archive. She also uses her iPhone heavily, often using it in reading rooms to take photos of documents and photos for her personal reference. She engages with her professional community on Twitter, and is also a heavy user of Instagram. 


## Isaac Hoffman, Data Scientist

<img src="../persona_images/isaacHoffman.jpg" alt="Image of Isaac Hoffman" width="500px"/>

Isaac is an expert in computational social science and focuses on research with tabular data sets. They want large and well-structured datasets that contain useful information. Isaac prefers working with open source tools since they can fully understand how they work and their affordances and limitations. They would like to work with a large email archive to understand interactions between individuals and topics at a high level.

#### Goals

- Isaac wants access to the complete set of data from emails, including the content and header metadata.
- Isaac wants to perform named-entity recognition and other lexical analysis techniques on large corpuses of email.



#### Pain points

- It is challenging for Isaac to extract text from PDF files with enough structure to be useful and the errors that likely come from this process may not make the data they are using representative and undermine their research.
- It is challenging for Isaac to work with datasets that do not have clear boundaries or provenance, as they risk undermining the representativeness of some of their methods.

#### Technology Use

Isaac is an expert at mining tabular data, and has a core set of tools they use for their research. They use a variety of hardware to support this work, including a number of high-powered desktop machines capable of running both Windows and Linux operating systems. They are adept with command-line use, and have a long history of contributing to open-source communities.

## Aaron Santos, Tool Maintainer

<img src="../persona_images/aaronSantos.jpg" alt="Image of Aaron Santos" width="500px"/>

Aaron is a technologist at a research university, primarily tasked with maintaining a web application for accessing born-digital records. The tool was originally funded by a national-level grant, but has since been maintained by the research university. Aaron is charged with devoting 80% of his time to maintaining the tool and 20% of his time maintaining the university’s library web applications. A community manager and designer at the university are also attached to the tool, but are only able to devote 20% of their time to the project. Funding for these positions comes primarily from the university with some support coming from the community. Aaron spends a lot of time updating the tool as its dependencies evolve. It was recently announced that the version of the primary framework that the tool relies on will reach its end-of-life in two years, so Aaron is now planning the update to the framework. He also spends a large amount of time following user forums and answering questions and responding to issues raised by the community.



#### Goals

- Aaron wants a common standard for serializing email in a stable format when it is not in active use by the web application.

#### Pain Points

- Aaron is concerned about using any technology that is not widely-adopted and would have to be replaced in the future due to lack of support.
- Aaron tries to avoid adding any dependencies to the tool’s stack, so he would like any tool to use the same technology.



#### Technology Use

Aaron has many years of experience working as a Linux system administrator. Although he is familiar with Windows environments, he strongly prefers to use his laptop, which runs Ubuntu. Aaron is active in a number of open source communities. 



## Gary Richardson, Self-Archivist

<img src="../persona_images/garyRichardson.jpg" alt="Image of Gary Richardson" width="300px"/>



Gary often communicates with his family online and wants to preserve his own email for future use. The email service he currently uses is going offline and he needs to export his email before the service shuts down. 

#### Goals

- Gary wants to preserve his email for later use
- Gary would like to browse email or attachments to find family photos
- Gary would like to browse and view his email without using additional tools.
- While Gary knows that the Mailbag tool will not enable him to search through his email for keywords, he wants his email package to preserve that potential if he is able to find other tools that enable search in the future.
- Gary wants an email package that’s easy to copy and paste so he can manage it along with other important files.

#### Pain Points

- Gary doesn’t have a lot of extra time to spare, so he needs clear, step-by-step documentation that will enable him to rapidly configure a tool without spending hours of time searching around the internet for fixes.
- While Gary has downloaded and configured desktop software in the past, he does not do it regularly, 



#### Technology Use

- Gary mostly uses an iPad to view and send email, but he also has a Windows laptop.
- Gary has downloaded and configured basic desktop software such as email clients in the past, but most of the tools he has found recently to fit his needs have been web applications. He has not yet had to do much configuration of desktop tools on his current version of Windows.
- Gary has never used command-line tools.