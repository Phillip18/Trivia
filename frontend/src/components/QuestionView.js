import React, { Component } from 'react';
import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import $ from 'jquery';

class QuestionView extends Component {
  constructor() {
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: {},
      currentCategory: null, // an integer
    };
  }

  componentDidMount() {
    this.getQuestions();
  }

  getQuestions = () => {
    this.state.oneCategory = false
    $.ajax({
      url: `/questions?page=${this.state.page}`,
      type: 'GET',
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          categories: result.categories,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again');
        return;
      },
    });
  };

  selectPage(num) {
    this.setState({ page: num }, () => {this.getQuestions()
    })
  }

  createPagination() {
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10);
      {for (let i = 1; i <= maxPage; i++) {
        pageNumbers.push(
          <span
            key={i}
            className={`page-num ${i === this.state.page ? 'active' : ''}`}
            onClick={() => {
              this.selectPage(i);
            }}
            // "oneCategory" means that the questions are given for a single category
            // in which case paginagion is not needed
            style = {this.state.oneCategory? {visibility: 'hidden'}: {visibility: 'visible'}}
          >
            {i}
          </span>
        );
      }}
    return pageNumbers;
  }

  getByCategory = (id) => {
    this.state.oneCategory = true // questions are from a single category
    this.state.currentCategory = id // record the current cagegory)
    $.ajax({
      url: '/category',
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({'category': id}),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
        });
        return;
      },
      error: (error) => {
        // no questions (not a real error)
        if (error.responseJSON.message == 'No questions in this category') {
          this.setState({
            questions: [],
            totalQuestions: 0
          })
        } else {
          // real error
          alert('Unable to load questions. Please try your request again');
        }
        return;
      },
    });
  };

  submitSearch = (searchTerm) => {
    $.ajax({
      url: `/search`,
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({ searchTerm: searchTerm}),
      xhrFields: {
        withCredentials: true,
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again');
        return;
      },
    });
  };

  questionAction = (id) => (action) => {
    if (action === 'DELETE') {
      if (window.confirm('are you sure you want to delete the question?')) {
        $.ajax({
          url: `/question/${id}`,
          type: 'DELETE',
          success: (result) => {
            if (!this.state.oneCategory) // if questions are not from a single category
              { 
                this.getQuestions(); 
              } else { 
                this.getByCategory(this.state.currentCategory); 
              }
          },
          error: (error) => {
            alert('Unable to load questions. Please try your request again');
            return;
          },
        });
      }
    }
  };

  render() {
      return (
        <div className='question-view'>
          <div className='categories-list'>
            <h2
              onClick={() => {
                this.getQuestions();
              }}
            >
              Categories
            </h2>
            <ul>
              {Object.keys(this.state.categories).map((id) => (
                <li
                  key={id}
                  onClick={() => {
                    this.getByCategory(id);
                  }}
                >
                  {this.state.categories[id]}
                  <img
                    className='category'
                    alt={`${this.state.categories[id].toLowerCase()}`}
                    src={`${this.state.categories[id].toLowerCase()}.svg`}
                  />
                </li>
                ))}
                </ul>
            {<Search submitSearch={this.submitSearch} />}
          </div>
          <div className='questions-list'>
            <h2>Questions</h2>
            {this.state.questions.map((q, ind) => {
              return(
              <Question
                key={q.id}
                question={q.question}
                answer={q.answer}
                category={this.state.categories[q.category]}
                difficulty={q.difficulty}
                questionAction={this.questionAction(q.id)}
            />
            )})}
            {<div className='pagination-menu'>{this.createPagination()}</div>}
          </div>
        </div>
      );
    }
  }

export default QuestionView;
