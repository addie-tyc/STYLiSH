# STYLiSH
** An e-commerce outfit website built by Flask with crawled Amazon products, recommendations of each and a dashboard of mock data stream **
* Built APIs by Flask RESTful
* Made a recommendation system by item-based collaborative filtering using cosine-similarity from 250,000+ Amazon reviews, and crawled some of those products’ information.
* Streamed mocked data from MongoDB, did data cleaning and saved cleaned data in MySQL every 5 seconds
* Designed a dashboard showing user behavior funnel and other metrics by Plotly.js in real-time

Website URL: https://stylish-addie.site

## Table of Contents
  * [Technologies](#technologies)
  * [Features](#features)

## Technologies

### Back-End
* Flask
* RESTful API
* Nginx

### Front-End
* HTML
* CSS
* JavaScript
* AJAX

### Database
* MySQL
* MongoDB

### Framework
* MVC
  
### Cloud Service
* AWS Elastic Compute Cloud (EC2)
* AWS Relational Database Service (RDS)
* AWS Simple Storage Service (S3)

### Networking
* HTTPS
* SSL
* Domain Name System (DNS)

## Features
* Dashboard
    - Made mock data and save them into MongoDB
    - Cleaned data and store into MySQL
    - Used SQL query calculate user behaviral data
    - Applied Plotly.js to build a dashboard of user funnel auto-refreshing every 5 seconds
![Dashboard](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/dashboard.png)
* Stylish
    - Made APIs by Flask RESTful
    - Bulit up web pages by AJAX
![Stylish](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/stylish.png)
* Recommendation
    - Constructed recommendation system by item-based collaborative filtering using 250,000+ Amazon products review
    - Crawled some of those products to build up a recommended page
![Recommendation](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/recommendation.png)

## Contact
Tsai-Yun Chung @ addiechung.tyc@gmail.com