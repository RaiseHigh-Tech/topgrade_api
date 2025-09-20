"""
Sample Data for TopGrade API
This file contains sample data for Programs, Advanced Programs, Categories, Syllabus, and Topics
Run this script to populate your database with test data
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topgrade.settings')
django.setup()

from topgrade_api.models import (
    Category, Program, AdvanceProgram, 
    Syllabus, Topic, AdvanceSyllabus, AdvanceTopic
)

def create_sample_data():
    """Create sample data for the application"""
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print("Clearing existing data...")
    Topic.objects.all().delete()
    AdvanceTopic.objects.all().delete()
    Syllabus.objects.all().delete()
    AdvanceSyllabus.objects.all().delete()
    Program.objects.all().delete()
    AdvanceProgram.objects.all().delete()
    Category.objects.all().delete()
    
    # Create Categories
    print("Creating categories...")
    categories_data = [
        {"name": "Web Development", "description": "Learn web development technologies", "icon": "🌐"},
        {"name": "Data Science", "description": "Master data science and analytics", "icon": "📊"},
        {"name": "Mobile Development", "description": "Build mobile applications", "icon": "📱"},
        {"name": "DevOps", "description": "Learn DevOps and cloud technologies", "icon": "☁️"},
        {"name": "AI & Machine Learning", "description": "Artificial Intelligence and ML", "icon": "🤖"},
        {"name": "Cybersecurity", "description": "Information security and ethical hacking", "icon": "🔒"},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category = Category.objects.create(**cat_data)
        categories[cat_data["name"]] = category
        print(f"Created category: {category.name}")
    
    # Create Regular Programs
    print("\nCreating regular programs...")
    programs_data = [
        {
            "title": "Full Stack Web Development Bootcamp",
            "subtitle": "Master MERN Stack Development",
            "description": "Complete full-stack web development course covering HTML, CSS, JavaScript, React, Node.js, Express, and MongoDB. Build real-world projects and deploy them to production.",
            "category": categories["Web Development"],
            "batch_starts": "Every Monday",
            "available_slots": 25,
            "duration": "16 weeks",
            "program_rating": Decimal("4.8"),
            "job_openings": "50,000+",
            "global_market_size": "$40B",
            "avg_annual_salary": "$85,000",
            "is_best_seller": True,
            "icon": "💻",
            "price": Decimal("599.00"),
            "discount_percentage": Decimal("20.00")
        },
        {
            "title": "Python Data Science Masterclass",
            "subtitle": "From Beginner to Data Scientist",
            "description": "Comprehensive data science course covering Python, NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn, and machine learning algorithms. Includes real-world projects and case studies.",
            "category": categories["Data Science"],
            "batch_starts": "1st & 15th of every month",
            "available_slots": 30,
            "duration": "12 weeks",
            "program_rating": Decimal("4.7"),
            "job_openings": "35,000+",
            "global_market_size": "$95B",
            "avg_annual_salary": "$95,000",
            "is_best_seller": True,
            "icon": "🐍",
            "price": Decimal("499.00"),
            "discount_percentage": Decimal("15.00")
        },
        {
            "title": "React Native Mobile App Development",
            "subtitle": "Build iOS & Android Apps",
            "description": "Learn to build cross-platform mobile applications using React Native. Cover navigation, state management, API integration, and app store deployment.",
            "category": categories["Mobile Development"],
            "batch_starts": "Every 2 weeks",
            "available_slots": 20,
            "duration": "10 weeks",
            "program_rating": Decimal("4.6"),
            "job_openings": "25,000+",
            "global_market_size": "$30B",
            "avg_annual_salary": "$78,000",
            "is_best_seller": False,
            "icon": "📱",
            "price": Decimal("449.00"),
            "discount_percentage": Decimal("10.00")
        },
        {
            "title": "DevOps Engineering Complete Course",
            "subtitle": "Master CI/CD and Cloud Technologies",
            "description": "Complete DevOps course covering Git, Docker, Kubernetes, Jenkins, AWS, Terraform, and monitoring tools. Learn to automate deployment pipelines.",
            "category": categories["DevOps"],
            "batch_starts": "Monthly",
            "available_slots": 15,
            "duration": "14 weeks",
            "program_rating": Decimal("4.9"),
            "job_openings": "40,000+",
            "global_market_size": "$25B",
            "avg_annual_salary": "$105,000",
            "is_best_seller": True,
            "icon": "⚙️",
            "price": Decimal("699.00"),
            "discount_percentage": Decimal("25.00")
        },
        {
            "title": "Cybersecurity Fundamentals",
            "subtitle": "Ethical Hacking & Security",
            "description": "Learn cybersecurity fundamentals, ethical hacking, penetration testing, and network security. Includes hands-on labs and real-world scenarios.",
            "category": categories["Cybersecurity"],
            "batch_starts": "Bi-weekly",
            "available_slots": 18,
            "duration": "8 weeks",
            "program_rating": Decimal("4.5"),
            "job_openings": "30,000+",
            "global_market_size": "$35B",
            "avg_annual_salary": "$90,000",
            "is_best_seller": False,
            "icon": "🔐",
            "price": Decimal("399.00"),
            "discount_percentage": Decimal("12.00")
        }
    ]
    
    programs = []
    for prog_data in programs_data:
        program = Program.objects.create(**prog_data)
        programs.append(program)
        print(f"Created program: {program.title}")
    
    # Create Advanced Programs
    print("\nCreating advanced programs...")
    advanced_programs_data = [
        {
            "title": "AI & Machine Learning Expert Track",
            "subtitle": "Advanced Deep Learning & Neural Networks",
            "description": "Advanced course covering deep learning, neural networks, computer vision, NLP, and AI deployment. Work on cutting-edge AI projects and research.",
            "batch_starts": "Quarterly",
            "available_slots": 12,
            "duration": "24 weeks",
            "program_rating": Decimal("4.9"),
            "job_openings": "20,000+",
            "global_market_size": "$190B",
            "avg_annual_salary": "$130,000",
            "is_best_seller": True,
            "icon": "🧠",
            "price": Decimal("1299.00"),
            "discount_percentage": Decimal("30.00")
        },
        {
            "title": "Enterprise Architecture & System Design",
            "subtitle": "Scalable Systems for Senior Engineers",
            "description": "Advanced system design course for senior engineers. Learn to design scalable, distributed systems, microservices architecture, and handle millions of users.",
            "batch_starts": "Monthly",
            "available_slots": 10,
            "duration": "20 weeks",
            "program_rating": Decimal("4.8"),
            "job_openings": "15,000+",
            "global_market_size": "$45B",
            "avg_annual_salary": "$150,000",
            "is_best_seller": True,
            "icon": "🏗️",
            "price": Decimal("999.00"),
            "discount_percentage": Decimal("20.00")
        },
        {
            "title": "Blockchain & Web3 Development",
            "subtitle": "Smart Contracts & DeFi Applications",
            "description": "Advanced blockchain development covering Ethereum, Solidity, smart contracts, DeFi protocols, and Web3 applications. Build decentralized applications from scratch.",
            "batch_starts": "Bi-monthly",
            "available_slots": 8,
            "duration": "18 weeks",
            "program_rating": Decimal("4.7"),
            "job_openings": "8,000+",
            "global_market_size": "$67B",
            "avg_annual_salary": "$120,000",
            "is_best_seller": False,
            "icon": "⛓️",
            "price": Decimal("899.00"),
            "discount_percentage": Decimal("15.00")
        }
    ]
    
    advanced_programs = []
    for adv_prog_data in advanced_programs_data:
        adv_program = AdvanceProgram.objects.create(**adv_prog_data)
        advanced_programs.append(adv_program)
        print(f"Created advanced program: {adv_program.title}")
    
    # Create Syllabus and Topics for Regular Programs
    print("\nCreating syllabus and topics for regular programs...")
    
    # Full Stack Web Development Syllabus
    web_dev_program = programs[0]
    web_syllabus_data = [
        {
            "module_title": "Frontend Fundamentals",
            "topics": [
                {"topic_title": "HTML5 Semantic Elements", "is_free_trail": True, "is_intro": True, "video_url": "https://example.com/html5"},
                {"topic_title": "CSS3 Flexbox and Grid", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/css3"},
                {"topic_title": "JavaScript ES6+ Features", "is_free_trail": True, "is_intro": False, "video_url": "https://example.com/js-es6"},
                {"topic_title": "DOM Manipulation", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/dom"},
            ]
        },
        {
            "module_title": "React Development",
            "topics": [
                {"topic_title": "React Components & JSX", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/react-intro"},
                {"topic_title": "State Management with Hooks", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/react-hooks"},
                {"topic_title": "React Router & Navigation", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/react-router"},
                {"topic_title": "Context API & Redux", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/redux"},
            ]
        },
        {
            "module_title": "Backend Development",
            "topics": [
                {"topic_title": "Node.js & Express Setup", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/nodejs"},
                {"topic_title": "RESTful API Development", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/rest-api"},
                {"topic_title": "MongoDB & Mongoose", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/mongodb"},
                {"topic_title": "Authentication & Authorization", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/auth"},
            ]
        },
        {
            "module_title": "Deployment & Production",
            "topics": [
                {"topic_title": "Docker Containerization", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/docker"},
                {"topic_title": "AWS Deployment", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/aws-deploy"},
                {"topic_title": "CI/CD Pipeline Setup", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/cicd"},
            ]
        }
    ]
    
    for syl_data in web_syllabus_data:
        syllabus = Syllabus.objects.create(
            program=web_dev_program,
            module_title=syl_data["module_title"]
        )
        
        for topic_data in syl_data["topics"]:
            Topic.objects.create(
                syllabus=syllabus,
                **topic_data
            )
        print(f"Created syllabus: {syllabus.module_title} with {len(syl_data['topics'])} topics")
    
    # Python Data Science Syllabus
    data_science_program = programs[1]
    ds_syllabus_data = [
        {
            "module_title": "Python Programming Basics",
            "topics": [
                {"topic_title": "Python Syntax & Variables", "is_free_trail": True, "is_intro": True, "video_url": "https://example.com/python-basics"},
                {"topic_title": "Data Types & Structures", "is_free_trail": True, "is_intro": False, "video_url": "https://example.com/python-data-types"},
                {"topic_title": "Control Flow & Functions", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/python-functions"},
            ]
        },
        {
            "module_title": "Data Analysis with Pandas",
            "topics": [
                {"topic_title": "Pandas DataFrames", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/pandas-intro"},
                {"topic_title": "Data Cleaning & Preprocessing", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/data-cleaning"},
                {"topic_title": "Data Visualization", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/data-viz"},
            ]
        },
        {
            "module_title": "Machine Learning",
            "topics": [
                {"topic_title": "Supervised Learning", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/supervised-ml"},
                {"topic_title": "Unsupervised Learning", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/unsupervised-ml"},
                {"topic_title": "Model Evaluation", "is_free_trail": False, "is_intro": False, "video_url": "https://example.com/model-eval"},
            ]
        }
    ]
    
    for syl_data in ds_syllabus_data:
        syllabus = Syllabus.objects.create(
            program=data_science_program,
            module_title=syl_data["module_title"]
        )
        
        for topic_data in syl_data["topics"]:
            Topic.objects.create(
                syllabus=syllabus,
                **topic_data
            )
        print(f"Created syllabus: {syllabus.module_title} with {len(syl_data['topics'])} topics")
    
    # Create Advanced Syllabus and Topics
    print("\nCreating syllabus and topics for advanced programs...")
    
    # AI & ML Expert Track Syllabus
    ai_program = advanced_programs[0]
    ai_syllabus_data = [
        {
            "module_title": "Deep Learning Fundamentals",
            "topics": [
                {"topic_title": "Neural Network Architecture", "video_url": "https://example.com/neural-networks"},
                {"topic_title": "Backpropagation Algorithm", "video_url": "https://example.com/backprop"},
                {"topic_title": "Gradient Descent Optimization", "video_url": "https://example.com/gradient-descent"},
                {"topic_title": "Regularization Techniques", "video_url": "https://example.com/regularization"},
            ]
        },
        {
            "module_title": "Computer Vision",
            "topics": [
                {"topic_title": "Convolutional Neural Networks", "video_url": "https://example.com/cnn"},
                {"topic_title": "Object Detection & Recognition", "video_url": "https://example.com/object-detection"},
                {"topic_title": "Image Segmentation", "video_url": "https://example.com/image-segmentation"},
                {"topic_title": "Transfer Learning", "video_url": "https://example.com/transfer-learning"},
            ]
        },
        {
            "module_title": "Natural Language Processing",
            "topics": [
                {"topic_title": "Text Preprocessing & Tokenization", "video_url": "https://example.com/text-preprocessing"},
                {"topic_title": "Word Embeddings & Word2Vec", "video_url": "https://example.com/word-embeddings"},
                {"topic_title": "Transformer Architecture", "video_url": "https://example.com/transformers"},
                {"topic_title": "BERT & GPT Models", "video_url": "https://example.com/bert-gpt"},
            ]
        },
        {
            "module_title": "AI Model Deployment",
            "topics": [
                {"topic_title": "Model Serving with FastAPI", "video_url": "https://example.com/model-serving"},
                {"topic_title": "Docker for ML Applications", "video_url": "https://example.com/docker-ml"},
                {"topic_title": "Cloud Deployment (AWS/GCP)", "video_url": "https://example.com/cloud-deploy"},
                {"topic_title": "MLOps Best Practices", "video_url": "https://example.com/mlops"},
            ]
        }
    ]
    
    for syl_data in ai_syllabus_data:
        advance_syllabus = AdvanceSyllabus.objects.create(
            advance_program=ai_program,
            module_title=syl_data["module_title"]
        )
        
        for topic_data in syl_data["topics"]:
            AdvanceTopic.objects.create(
                advance_syllabus=advance_syllabus,
                **topic_data
            )
        print(f"Created advanced syllabus: {advance_syllabus.module_title} with {len(syl_data['topics'])} topics")
    
    # System Design Advanced Program Syllabus
    system_design_program = advanced_programs[1]
    sd_syllabus_data = [
        {
            "module_title": "Scalability Fundamentals",
            "topics": [
                {"topic_title": "Load Balancing Strategies", "video_url": "https://example.com/load-balancing"},
                {"topic_title": "Horizontal vs Vertical Scaling", "video_url": "https://example.com/scaling"},
                {"topic_title": "Caching Mechanisms", "video_url": "https://example.com/caching"},
                {"topic_title": "Database Sharding", "video_url": "https://example.com/sharding"},
            ]
        },
        {
            "module_title": "Microservices Architecture",
            "topics": [
                {"topic_title": "Service Decomposition", "video_url": "https://example.com/microservices"},
                {"topic_title": "API Gateway Design", "video_url": "https://example.com/api-gateway"},
                {"topic_title": "Inter-service Communication", "video_url": "https://example.com/service-comm"},
                {"topic_title": "Service Discovery", "video_url": "https://example.com/service-discovery"},
            ]
        },
        {
            "module_title": "Distributed Systems",
            "topics": [
                {"topic_title": "CAP Theorem", "video_url": "https://example.com/cap-theorem"},
                {"topic_title": "Consensus Algorithms", "video_url": "https://example.com/consensus"},
                {"topic_title": "Event-Driven Architecture", "video_url": "https://example.com/event-driven"},
                {"topic_title": "Message Queues & Kafka", "video_url": "https://example.com/message-queues"},
            ]
        }
    ]
    
    for syl_data in sd_syllabus_data:
        advance_syllabus = AdvanceSyllabus.objects.create(
            advance_program=system_design_program,
            module_title=syl_data["module_title"]
        )
        
        for topic_data in syl_data["topics"]:
            AdvanceTopic.objects.create(
                advance_syllabus=advance_syllabus,
                **topic_data
            )
        print(f"Created advanced syllabus: {advance_syllabus.module_title} with {len(syl_data['topics'])} topics")
    
    print("\n✅ Sample data creation completed!")
    print(f"Created {Category.objects.count()} categories")
    print(f"Created {Program.objects.count()} regular programs")
    print(f"Created {AdvanceProgram.objects.count()} advanced programs")
    print(f"Created {Syllabus.objects.count()} regular syllabi")
    print(f"Created {AdvanceSyllabus.objects.count()} advanced syllabi")
    print(f"Created {Topic.objects.count()} regular topics")
    print(f"Created {AdvanceTopic.objects.count()} advanced topics")

if __name__ == "__main__":
    create_sample_data()