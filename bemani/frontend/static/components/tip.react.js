/** @jsx React.DOM */

var Tip = React.createClass({
    render: function() {
        return (
            <div className="tooltip">
                {this.props.children}
                <span className="tooltiptext">{this.props.text}</span>
            </div>
        );
    },
});
