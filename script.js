// Configure application
function configure()
{
    // Configure typeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                "<div>"+
                "{{Title}}, {{Author}}" +
                "</div>"
            )
       }
    });


    // Give focus to text box
    $("#q").focus();
}

// Search database for typeahead's suggestions
function search(query, syncResults, asyncResults)
{
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };
    $.getJSON("/adjust", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (Author Title)
        asyncResults(data);
    });


}

$(document).ready(function() {
   configure();
});