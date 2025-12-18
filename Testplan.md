# TestPlan – Learning Path Recommender

This document lists sample test cases for the Learning Path Recommender system.

## Test Cases Overview

| TC ID | Type     | Description                                              Input                                                                                               Expected Result                                                                                                                                                     | Actual Result |

| TC-01 | Normal   | Beginner user wants to become a junior web developer    | Current skills: HTML basics; Background: 1st-year CS student; Time: 7 hrs/week; Goal: Junior Web Dev | System generates a 4–6 week roadmap with HTML/CSS refresh, basic JS, simple project tasks; learning path is well-ordered and fits within ~7 hrs/week.               | TBD           |
| TC-02 | Positive | User provides clear, rich input for data analysis goal  | Current skills: Excel, basic statistics; Background: BBA; Time: 10 hrs/week; Goal: Data Analysis    | System outputs a detailed, tailored path (Python basics, Pandas, data visualization) with weekly milestones and relevant resources; no validation errors are shown. | TBD           |
| TC-03 | Negative | Missing/invalid input (no time availability provided)   | Current skills: None; Background: Non-technical; Time: *empty*; Goal: Learn Python basics           | System prompts user with a clear validation message asking to provide time availability; roadmap is **not** generated until valid time is supplied.                | TBD           |
| TC-04 | Edge     | Very limited time but ambitious goal                    | Current skills: None; Background: Non-technical; Time: 1 hr/week; Goal: Junior Web Dev              | System warns that the goal may take longer than 4–6 weeks; generates a minimal starter roadmap focusing on fundamentals and sets realistic expectations.           | TBD           |
| TC-05 | Edge     | Highly experienced user close to target goal            | Current skills: HTML, CSS, JS, basic React; Background: 2 years freelancing; Time: 15 hrs/week; Goal: Junior Web Dev | System generates a short, advanced-focused path (React projects, Git, basic testing, portfolio building) and compresses roadmap to fewer weeks with deeper tasks. | TBD           |


