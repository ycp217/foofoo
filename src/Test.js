/* jshint esnext:true */
let React = require('react');
let request = require('superagent');

let Test = React.createClass({
	componentWillMount: function() {
		request
		.get('http://127.0.0.1:5000/api/people')
		.accept('application/json')
		.end( function(err, res){
			if (res.status === 200) {
				console.log(res.text);
			}
		});

	},
	render: function() {
		return (
			<div>
			<h1>Test</h1>
			</div>
		)
	}
});

module.exports = Test;
