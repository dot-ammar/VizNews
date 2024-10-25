document.addEventListener('DOMContentLoaded', function() {

    const storedData = JSON.parse(localStorage.getItem('apiData'));
    
    articles = storedData.articles;
    num_of_sources = storedData.numSources;
    num_of_articles = storedData.numArticles;
    avgPolarity = parseFloat(storedData.average_polarity.toFixed(3));
    avgSubjectivity = (parseFloat(storedData.average_subjectivity) * 100).toFixed(2); 

    document.getElementById('num_of_sources').textContent = num_of_sources;
    document.getElementById('num_of_articles').textContent = num_of_articles;
    document.getElementById('avgPolarity').textContent = avgPolarity;
    document.getElementById('avgSubjectivity').textContent = avgSubjectivity + '%';

})

