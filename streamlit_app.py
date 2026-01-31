"""
Streamlit Frontend for Quiz Generator API
"""
import streamlit as st
import requests
import json

API_URL = "http://localhost:8004"

st.set_page_config(page_title="Quiz Generator", page_icon="📝", layout="wide")

# Initialize session state
if "result" not in st.session_state:
    st.session_state["result"] = None
if "ocr_result" not in st.session_state:
    st.session_state["ocr_result"] = None
if "checking_result" not in st.session_state:
    st.session_state["checking_result"] = None

# Main title
st.title("📝 Quiz & Assignment Generator")

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["🎯 Generate Quiz/Assignment", "📷 OCR - Extract Answers", "✅ Check Papers"])

# ============== TAB 1: QUIZ GENERATION ==============
with tab1:
    st.markdown("Upload documents and generate quizzes and assignments automatically.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Configuration")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Documents (PDF, DOCX)",
            type=["pdf", "docx", "doc"],
            accept_multiple_files=True,
            key="quiz_files"
        )
        
        st.markdown("---")
        st.markdown("**Quiz Settings**")
        num_quizzes = st.number_input("Number of Quizzes", min_value=0, max_value=10, value=1)
        mcq_count = st.number_input("MCQ Questions per Quiz", min_value=0, max_value=20, value=5)
        fill_blanks_count = st.number_input("Fill in Blanks per Quiz", min_value=0, max_value=20, value=3)
        true_false_count = st.number_input("True/False per Quiz", min_value=0, max_value=20, value=2)
        quiz_difficulty = st.selectbox("Quiz Difficulty", ["easy", "medium", "hard"], index=1, key="quiz_diff")
        
        st.markdown("---")
        st.markdown("**Assignment Settings**")
        num_assignments = st.number_input("Number of Assignments", min_value=0, max_value=10, value=0)
        assignment_questions = st.number_input("Questions per Assignment", min_value=1, max_value=20, value=5)
        assignment_difficulty = st.selectbox("Assignment Difficulty", ["easy", "medium", "hard"], index=1, key="assign_diff")
        
        st.markdown("---")
        delete_index_after = st.checkbox("Delete index after generation", value=True)
        
        # Generate button
        if st.button("🚀 Generate", type="primary", use_container_width=True):
            if not uploaded_files:
                st.error("Please upload at least one document.")
            else:
                with st.spinner("Processing documents and generating content..."):
                    try:
                        files = [
                            ("files", (f.name, f.getvalue(), f.type))
                            for f in uploaded_files
                        ]
                        
                        data = {
                            "num_quizzes": num_quizzes,
                            "num_assignments": num_assignments,
                            "mcq_count": mcq_count,
                            "fill_blanks_count": fill_blanks_count,
                            "true_false_count": true_false_count,
                            "quiz_difficulty": quiz_difficulty,
                            "assignment_questions": assignment_questions,
                            "assignment_difficulty": assignment_difficulty,
                            "delete_index_after": delete_index_after
                        }
                        
                        response = requests.post(
                            f"{API_URL}/generate",
                            files=files,
                            data=data,
                            timeout=300
                        )
                        
                        result = response.json()
                        
                        if result.get("success"):
                            st.success(result.get("message"))
                            st.session_state["result"] = result
                        else:
                            st.error(f"Error: {result.get('message')}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to API. Make sure FastAPI is running on port 8004.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col2:
        st.subheader("📄 Results")
        
        if st.session_state["result"]:
            result = st.session_state["result"]
            
            # Download buttons - fetch docs and show download buttons directly
            st.markdown("**📥 Download Documents**")
            download_col1, download_col2, download_col3 = st.columns(3)
            
            with download_col1:
                if result.get("quizzes"):
                    try:
                        quiz_response = requests.post(
                            f"{API_URL}/download/quiz",
                            json={"quizzes": result["quizzes"], "assignments": []},
                            timeout=60
                        )
                        if quiz_response.status_code == 200:
                            st.download_button(
                                "📥 Download Quizzes",
                                data=quiz_response.content,
                                file_name="quizzes.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="dl_quiz"
                            )
                    except Exception as e:
                        st.error(f"Quiz doc error: {e}")
            
            with download_col2:
                if result.get("assignments"):
                    try:
                        assign_response = requests.post(
                            f"{API_URL}/download/assignment",
                            json={"quizzes": [], "assignments": result["assignments"]},
                            timeout=60
                        )
                        if assign_response.status_code == 200:
                            st.download_button(
                                "📥 Download Assignments",
                                data=assign_response.content,
                                file_name="assignments.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="dl_assign"
                            )
                    except Exception as e:
                        st.error(f"Assignment doc error: {e}")
            
            with download_col3:
                if result.get("quizzes") or result.get("assignments"):
                    try:
                        combined_response = requests.post(
                            f"{API_URL}/download/combined",
                            json={"quizzes": result.get("quizzes", []), "assignments": result.get("assignments", [])},
                            timeout=60
                        )
                        if combined_response.status_code == 200:
                            st.download_button(
                                "📥 Download All",
                                data=combined_response.content,
                                file_name="quiz_assignment_package.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="dl_combined"
                            )
                    except Exception as e:
                        st.error(f"Combined doc error: {e}")
            
            st.markdown("---")
            
            # Tabs for viewing results
            result_tab1, result_tab2, result_tab3 = st.tabs(["📋 Quizzes", "📝 Assignments", "📊 Raw JSON"])
            
            with result_tab1:
                quizzes = result.get("quizzes", [])
                if quizzes:
                    for quiz in quizzes:
                        st.markdown(f"### Quiz {quiz['quiz_number']} (Total Marks: {quiz['total_marks']})")
                        
                        for q in quiz["questions"]:
                            with st.expander(f"Q{q['question_number']}: {q['question_text'][:60]}..."):
                                st.markdown(f"**Question:** {q['question_text']}")
                                st.markdown(f"**Type:** {q['question_type']} | **Marks:** {q['marks']} | **Difficulty:** {q['difficulty_level']}")
                                
                                if q.get("options"):
                                    st.markdown("**Options:**")
                                    for opt in q["options"]:
                                        st.markdown(f"- {opt}")
                                
                                st.markdown(f"✅ **Correct Answer:** {q['correct_answer']}")
                                
                                if q.get("explanation"):
                                    st.markdown(f"💡 **Explanation:** {q['explanation']}")
                        
                        st.markdown("---")
                else:
                    st.info("No quizzes generated.")
            
            with result_tab2:
                assignments = result.get("assignments", [])
                if assignments:
                    for assignment in assignments:
                        st.markdown(f"### Assignment {assignment['assignment_number']} (Total Marks: {assignment['total_marks']})")
                        
                        for q in assignment["questions"]:
                            with st.expander(f"Q{q['question_number']}: {q['question_text'][:60]}..."):
                                st.markdown(f"**Question:** {q['question_text']}")
                                st.markdown(f"**Type:** {q['question_type']} | **Marks:** {q['marks']} | **Difficulty:** {q['difficulty_level']}")
                                
                                if q.get("expected_length"):
                                    st.markdown(f"📏 **Expected Length:** {q['expected_length']}")
                                
                                if q.get("key_points"):
                                    st.markdown("🔑 **Key Points:**")
                                    for point in q["key_points"]:
                                        st.markdown(f"- {point}")
                        
                        st.markdown("---")
                else:
                    st.info("No assignments generated.")
            
            with result_tab3:
                st.json(result)
        else:
            st.info("Upload documents and click Generate to see results here.")


# ============== TAB 2: OCR ==============
with tab2:
    st.markdown("Extract handwritten answers from documents using AI Vision.")
    
    ocr_col1, ocr_col2 = st.columns([1, 2])
    
    with ocr_col1:
        st.subheader("📤 Upload or Link")
        
        ocr_method = st.radio("Choose input method:", ["Upload Files", "Google Drive Link"])
        
        if ocr_method == "Upload Files":
            ocr_files = st.file_uploader(
                "Upload answer sheets (PDF, Images)",
                type=["pdf", "png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key="ocr_files"
            )
            
            if st.button("🔍 Extract Answers", type="primary", use_container_width=True, key="ocr_upload_btn"):
                if not ocr_files:
                    st.error("Please upload at least one file.")
                else:
                    with st.spinner("Extracting handwritten text..."):
                        try:
                            files = [
                                ("files", (f.name, f.getvalue(), f.type))
                                for f in ocr_files
                            ]
                            
                            response = requests.post(
                                f"{API_URL}/ocr/extract",
                                files=files,
                                timeout=300
                            )
                            
                            result = response.json()
                            
                            if result.get("success"):
                                st.success(f"✅ Extracted {result.get('total_answers', 0)} answers from {result.get('total_files', 0)} files")
                                st.session_state["ocr_result"] = result
                            else:
                                st.error(f"Error: {result.get('error')}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API. Make sure FastAPI is running on port 8004.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        else:  # Google Drive Link
            drive_url = st.text_input("Enter Google Drive link:", placeholder="https://drive.google.com/drive/folders/... or /file/d/...")
            
            if st.button("🔍 Extract from Drive", type="primary", use_container_width=True, key="ocr_drive_btn"):
                if not drive_url:
                    st.error("Please enter a Google Drive link.")
                else:
                    with st.spinner("Downloading and extracting text (this may take a while for folders)..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/ocr/extract-url",
                                data={"drive_url": drive_url},
                                timeout=600  # 10 minutes for large folders
                            )
                            
                            result = response.json()
                            
                            if result.get("success"):
                                st.success(f"✅ Extracted {result.get('total_answers', 0)} answers from {result.get('total_files', 0)} files")
                                st.session_state["ocr_result"] = result
                            else:
                                st.error(f"Error: {result.get('error')}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API. Make sure FastAPI is running on port 8004.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    with ocr_col2:
        st.subheader("📝 Extracted Answers")
        
        if st.session_state["ocr_result"]:
            ocr_result = st.session_state["ocr_result"]
            files_data = ocr_result.get("files_data", [])
            
            if files_data:
                # Summary
                st.markdown(f"**📊 Summary:** {len(files_data)} files, {ocr_result.get('total_pages', 0)} pages, {ocr_result.get('total_answers', 0)} answers")
                
                # Download button for ZIP of Word docs - direct download
                st.markdown("---")
                try:
                    zip_response = requests.post(
                        f"{API_URL}/ocr/download",
                        json={"files_data": files_data},
                        timeout=120
                    )
                    if zip_response.status_code == 200:
                        st.download_button(
                            "📥 Download All as Word Documents (ZIP)",
                            data=zip_response.content,
                            file_name="student_answers.zip",
                            mime="application/zip",
                            use_container_width=True,
                            type="primary",
                            key="dl_ocr_zip"
                        )
                    else:
                        st.error("Failed to generate documents")
                except Exception as e:
                    st.error(f"Download error: {e}")
                
                st.markdown("---")
                
                # Display each file separately
                for file_data in files_data:
                    filename = file_data.get('filename', 'Unknown')
                    answers = file_data.get('answers', [])
                    quiz_answers = file_data.get('quiz_answers', [])
                    raw_text = file_data.get('raw_text', '')
                    pages = file_data.get('pages_processed', 0)
                    
                    with st.expander(f"📄 {filename} ({len(answers)} answers, {pages} pages)", expanded=False):
                        
                        if file_data.get('error'):
                            st.error(f"Error: {file_data.get('error')}")
                            continue
                        
                        # RAW TEXT FIRST - so user can see what was extracted
                        if raw_text:
                            st.markdown("#### 📝 Complete Extracted Text (Raw)")
                            st.info("This is ALL the text extracted from the document before structuring into answers:")
                            st.text_area(
                                "Raw Text",
                                value=raw_text,
                                height=300,
                                key=f"raw_{filename}",
                                disabled=True
                            )
                            st.markdown("---")
                        
                        # Structured Answers for this file
                        if answers:
                            st.markdown("#### ✅ Structured Answers")
                            for answer in answers:
                                ans_num = answer.get('answer_number', '?')
                                ans_type = answer.get('answer_type', 'unknown')
                                content = answer.get('content', 'No content')
                                confidence = answer.get('confidence', 'N/A')
                                
                                st.markdown(f"**Answer {ans_num}** ({ans_type})")
                                st.text_area(
                                    f"Content",
                                    value=content,
                                    height=100,
                                    key=f"{filename}_{ans_num}",
                                    disabled=True
                                )
                                st.caption(f"Confidence: {confidence}")
                                st.markdown("---")
                        
                        # Quiz answers for this file
                        if quiz_answers:
                            st.markdown("#### 🔘 Quiz/MCQ Answers")
                            for qa in quiz_answers:
                                st.markdown(f"**Q{qa.get('question_number', '?')}:** {qa.get('answer', 'N/A')}")
                        
                        # Raw JSON for this file
                        with st.expander("🔍 View Raw JSON for this file"):
                            st.json(file_data)
                
                st.markdown("---")
                
                # Full raw JSON
                with st.expander("📊 View Complete Raw JSON"):
                    st.json(ocr_result)
            else:
                st.warning("No files data found in result")
        else:
            st.info("Upload answer sheets or provide a Google Drive link to extract answers.")


# ============== TAB 3: PAPER CHECKING ==============
with tab3:
    st.markdown("Grade student papers against an answer key using AI semantic comparison.")
    st.info("💡 **How it works:** Upload answer key + student papers → AI grades semantically (meaning-based, not word-for-word) → Download Excel results")
    
    check_col1, check_col2 = st.columns([1, 2])
    
    with check_col1:
        st.subheader("📤 Upload Files")
        
        # Answer key upload
        st.markdown("**1️⃣ Answer Key**")
        answer_key_file = st.file_uploader(
            "Upload Answer Key (PDF/DOCX)",
            type=["pdf", "docx", "doc"],
            key="answer_key"
        )
        
        st.markdown("---")
        
        # Method selection
        check_method = st.radio(
            "**2️⃣ Student Papers Source:**",
            ["Upload Files", "Google Drive Link"],
            key="check_method"
        )
        
        if check_method == "Upload Files":
            student_papers = st.file_uploader(
                "Upload Student Papers (PDF)",
                type=["pdf"],
                accept_multiple_files=True,
                key="student_papers"
            )
            
            if st.button("🔍 Check Papers", type="primary", use_container_width=True, key="check_upload_btn"):
                if not answer_key_file:
                    st.error("Please upload an answer key file.")
                elif not student_papers:
                    st.error("Please upload at least one student paper.")
                else:
                    with st.spinner("Processing answer key and grading papers... This may take a few minutes."):
                        try:
                            # Prepare files
                            files = [
                                ("answer_key", (answer_key_file.name, answer_key_file.getvalue(), answer_key_file.type))
                            ]
                            
                            # Add student papers
                            for paper in student_papers:
                                files.append(("student_papers", (paper.name, paper.getvalue(), paper.type)))
                            
                            # Send request
                            response = requests.post(
                                f"{API_URL}/check-papers/upload",
                                files=files,
                                timeout=600  # 10 minutes for multiple papers
                            )
                            
                            result = response.json()
                            
                            if result.get("success"):
                                st.success(f"✅ Graded {result.get('successful', 0)} out of {result.get('total_students', 0)} papers successfully!")
                                st.session_state["checking_result"] = result
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API. Make sure FastAPI is running on port 8004.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        else:  # Google Drive
            drive_url = st.text_input(
                "Google Drive Link:",
                placeholder="https://drive.google.com/drive/folders/...",
                key="check_drive_url"
            )
            
            if st.button("🔍 Check Papers from Drive", type="primary", use_container_width=True, key="check_drive_btn"):
                if not answer_key_file:
                    st.error("Please upload an answer key file.")
                elif not drive_url:
                    st.error("Please enter a Google Drive link.")
                else:
                    with st.spinner("Downloading from Google Drive and grading papers... This may take a while."):
                        try:
                            # Prepare answer key file
                            files = [
                                ("answer_key", (answer_key_file.name, answer_key_file.getvalue(), answer_key_file.type))
                            ]
                            
                            data = {"drive_url": drive_url}
                            
                            # Send request
                            response = requests.post(
                                f"{API_URL}/check-papers/drive",
                                files=files,
                                data=data,
                                timeout=900  # 15 minutes for large folders
                            )
                            
                            result = response.json()
                            
                            if result.get("success"):
                                st.success(f"✅ Graded {result.get('successful', 0)} out of {result.get('total_students', 0)} papers successfully!")
                                st.session_state["checking_result"] = result
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API. Make sure FastAPI is running on port 8004.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    with check_col2:
        st.subheader("📊 Grading Results")
        
        if st.session_state["checking_result"]:
            result = st.session_state["checking_result"]
            
            # Summary stats
            st.markdown("### 📈 Summary")
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                st.metric("Total Students", result.get('total_students', 0))
            with summary_col2:
                st.metric("Successful", result.get('successful', 0), delta=None)
            with summary_col3:
                st.metric("Failed", result.get('failed', 0), delta=None)
            with summary_col4:
                assessment_type = result.get('assessment_type', 'assignment')
                st.metric("Type", assessment_type.title())
            
            # Answer key info
            answer_key_info = result.get('answer_key_info', {})
            if answer_key_info:
                st.markdown(f"**Answer Key:** {answer_key_info.get('total_questions', 0)} questions, {answer_key_info.get('total_marks', 0)} total marks")
            
            st.markdown("---")
            
            # Download Excel button
            st.markdown("### 📥 Download Results")
            try:
                excel_response = requests.post(
                    f"{API_URL}/check-papers/download-excel",
                    json={"checking_results": result},
                    timeout=120
                )
                if excel_response.status_code == 200:
                    st.download_button(
                        "📊 Download Excel Spreadsheet",
                        data=excel_response.content,
                        file_name="grading_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary",
                        key="dl_excel"
                    )
                    st.caption("Excel includes: Name, Roll Number, marks per answer, and total marks")
                else:
                    st.error("Failed to generate Excel file")
            except Exception as e:
                st.error(f"Excel download error: {e}")
            
            st.markdown("---")
            
            # Results tabs
            result_tab1, result_tab2 = st.tabs(["📋 Student Results", "📊 Raw JSON"])
            
            with result_tab1:
                results = result.get('results', [])
                
                if results:
                    for idx, student_result in enumerate(results, 1):
                        # Student card
                        with st.expander(
                            f"👤 {student_result.get('student_name', 'Unknown')} - {student_result.get('roll_number', 'Unknown')} | "
                            f"Score: {student_result.get('total_obtained', 0)}/{student_result.get('total_max', 0)}",
                            expanded=False
                        ):
                            # Student info
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.markdown(f"**File:** {student_result.get('filename', 'Unknown')}")
                                st.markdown(f"**Answers Extracted:** {student_result.get('answers_extracted', 0)}")
                            with col_info2:
                                st.markdown(f"**Total Obtained:** {student_result.get('total_obtained', 0)}")
                                st.markdown(f"**Total Max:** {student_result.get('total_max', 0)}")
                            
                            # Error case
                            if not student_result.get('success'):
                                st.error(f"❌ Error: {student_result.get('error', 'Unknown error')}")
                                continue
                            
                            # Grading details
                            grading = student_result.get('grading', {})
                            evaluations = grading.get('evaluations', [])
                            
                            if evaluations:
                                st.markdown("#### 📝 Answer-by-Answer Breakdown")
                                
                                for eval_item in evaluations:
                                    q_num = eval_item.get('question_number', '?')
                                    obtained = eval_item.get('obtained_marks', 0)
                                    max_marks = eval_item.get('max_marks', 0)
                                    feedback = eval_item.get('feedback', '')
                                    is_correct = eval_item.get('is_correct')
                                    
                                    # Color code based on performance
                                    percentage = (obtained / max_marks * 100) if max_marks > 0 else 0
                                    
                                    if percentage == 100:
                                        status_icon = "✅"
                                        status_color = "green"
                                    elif percentage >= 50:
                                        status_icon = "⚠️"
                                        status_color = "orange"
                                    else:
                                        status_icon = "❌"
                                        status_color = "red"
                                    
                                    st.markdown(f"**{status_icon} Question {q_num}:** {obtained}/{max_marks} marks ({percentage:.0f}%)")
                                    
                                    if feedback:
                                        st.caption(f"💬 {feedback}")
                                    
                                    if is_correct is not None:
                                        st.caption(f"Correct: {'✅ Yes' if is_correct else '❌ No'}")
                                    
                                    st.markdown("---")
                            
                            # Overall feedback
                            overall_feedback = grading.get('overall_feedback', '')
                            if overall_feedback:
                                st.markdown("#### 💬 Overall Feedback")
                                st.info(overall_feedback)
                else:
                    st.warning("No results found")
            
            with result_tab2:
                st.json(result)
        else:
            st.info("👆 Upload answer key and student papers, then click 'Check Papers' to see results here.")


# ============== SIDEBAR: INDEX MANAGEMENT ==============
st.sidebar.markdown("---")
st.sidebar.subheader("🗂️ Index Management")

if st.sidebar.button("List Indexes"):
    try:
        response = requests.get(f"{API_URL}/indexes")
        data = response.json()
        if data.get("success"):
            st.sidebar.write(f"Found {data.get('count', 0)} indexes:")
            for idx in data.get("indexes", []):
                st.sidebar.write(f"- {idx['name']}")
        else:
            st.sidebar.error(data.get("error"))
    except requests.exceptions.ConnectionError:
        st.sidebar.error("API not running")

index_to_delete = st.sidebar.text_input("Index name to delete")
if st.sidebar.button("Delete Index"):
    if index_to_delete:
        try:
            response = requests.delete(f"{API_URL}/indexes/{index_to_delete}")
            data = response.json()
            if data.get("success"):
                st.sidebar.success(data.get("message"))
            else:
                st.sidebar.error(data.get("error"))
        except requests.exceptions.ConnectionError:
            st.sidebar.error("API not running")

# Health check
st.sidebar.markdown("---")
try:
    health = requests.get(f"{API_URL}/health", timeout=2)
    if health.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Error")
except:
    st.sidebar.error("❌ API Offline")
