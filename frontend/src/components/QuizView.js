import React, { Component } from 'react';
import $ from 'jquery';
import '../stylesheets/QuizView.css';

const questionsPerPlay = 5;

class QuizView extends Component {
  constructor(props) {
    super();
    this.state = {
      quizCategory: null,
      previousQuestions: [],
      showAnswer: false,
      categories: {},
      numCorrect: 0,
      question: '',
      answer: '',
      guess: '',
      evaluate: false, // evaluation mode
      end: false // end of game
    };
  }

  componentDidMount() {
    $.ajax({
      url: `/categories`,
      type: 'GET',
      success: (result) => {
        this.setState({ categories: result.categories });
        return;
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again');
        return;
      },
    });
  }

  selectCategory = ({ type, id = 0 }) => {
    this.setState({ quizCategory: { type, id } }, this.getNextQuestion);
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value });
  };

  getNextQuestion = () => {
    $.ajax({
      url: '/quiz', //TODO: update request URL
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        previous_questions: this.state.previousQuestions,
        quiz_category: this.state.quizCategory,
      }),
      xhrFields: {
        withCredentials: true,
      },
      crossDomain: true,
      success: (question) => {
        this.setState({
          showAnswer: false,
          question: question.question,
          answer: question.answer,
          questionId: question.id,
          guess: '',
          end: question.question == 'none'? true : false // if no more questions, the game ends
        });
        this.state.previousQuestions.push(this.state.questionId);
        this.render()
        return;
      },
      error: (error) => {
        console.log(error)
        alert('Unable to load question. Please try your request again');
        return;
      },
    });
  };

  submitGuess = (event) => {
    event.preventDefault();
    this.state.evaluate = this.evaluateAnswer();
    this.setState({
      numCorrect: !this.state.evaluate ? this.state.numCorrect : this.state.numCorrect + 1,
      showAnswer: true,
    });
  };

  restartGame = () => {
    this.setState({
      quizCategory: null,
      previousQuestions: [],
      showAnswer: false,
      numCorrect: 0,
      question: '',
      answer: '',
      questionId: 0,
      guess: '',
      end: false,
    });
  };

  renderPrePlay() {
    return (
      <div className='quiz-play-holder'>
        <div className='choose-header'>Choose Category</div>
        <div className='category-holder'>
          <div className='play-category' onClick={this.selectCategory}>
            ALL
          </div>
          {Object.keys(this.state.categories).map((id) => {
            return (
              <div
                key={id}
                value={id}
                className='play-category'
                onClick={() =>
                  this.selectCategory({ type: this.state.categories[id], id })
                }
              >
                {this.state.categories[id]}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  renderFinalScore() {
    return (
      <div className='quiz-play-holder'>
        <div className='final-header'>
          Your Final Score is {this.state.numCorrect}
        </div>
        <div className='play-again button' onClick={this.restartGame}>
          Play Again?
        </div>
      </div>
    );
  }

  evaluateAnswer = () => {
    const formatGuess = this.state.guess
      // eslint-disable-next-line
      .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, '')
      .toLowerCase();
    const answerArray = this.state.answer
      .toLowerCase()
      .split(' ');
    return answerArray.every((el) => formatGuess.includes(el));
  };

  renderCorrectAnswer() {
    return (
      <div className='quiz-play-holder'>
        <div className='quiz-question'>
          {this.state.question}
        </div>
        <div className={`${this.state.evaluate ? 'correct' : 'wrong'}`}>
          {this.state.evaluate ? 'You were correct!' : 'You were incorrect'}
        </div>
        <div className='quiz-answer'>{this.state.answer}</div>
        <div className='next-question button' onClick={ () => {
          if (this.state.previousQuestions.length == questionsPerPlay) {
            this.setState({end: true})
          } else {
            this.getNextQuestion()
          }
          }
        }
          >
          {' '}
          {this.state.previousQuestions.length != questionsPerPlay ? 'Next Question' : 'See Score' }
          {' '}
        </div>
      </div>
    );
  }

  renderPlay() {
    return  this.state.end ? (
      this.renderFinalScore()
    ) : this.state.showAnswer ? (
      this.renderCorrectAnswer()
    ) : (
      <div className='quiz-play-holder'>
        <div className='quiz-question'>
          {this.state.question}
        </div>
        <form onSubmit={this.submitGuess}>
          <input type='text' name='guess' onChange={this.handleChange} />
          <input
            className='submit-guess button'
            type='submit'
            value='Submit Answer'
          />
        </form>
      </div>
    );
  }

  render() {
    return this.state.quizCategory ? this.renderPlay() : this.renderPrePlay();
  }
}

export default QuizView;
