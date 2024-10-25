var projectTemplatesSet;
document.addEventListener('DOMContentLoaded', async function() {


  if (window.location.pathname.includes('projects.html')) {
    showLoadingSpinner(); // Show loading spinner
    var name = getCookie('name');
    var skill = getCookie('skill');
    var languages = getCookie('languages');
    var frameworks = getCookie('frameworks');
    var interests = getCookie('interests');
    var apiKey = getCookie('apiKey');
    projectTemplatesSet = await setProject(name, skill, languages, frameworks, interests, apiKey);

  }


  if (window.location.pathname.includes('assessment.html')) {
    document.getElementById('regForm').addEventListener('submit', function(event) {
        event.preventDefault(); 
        saveFormData();
        nextPage();
        
    });
  } 

  if (window.location.pathname.includes('finalProject.html')) {
    selectedProject = getCookie('selectedProject');
    finalProjectTemplate = JSON.parse(getCookie('projectTemplate'));
    document.getElementById('Title').innerHTML = finalProjectTemplate.Title;
    document.getElementById('description').innerHTML = finalProjectTemplate["Long Description"];
    try{
    let toolsContent = '<ul>';
    finalProjectTemplate["Tools and Requirements"].forEach(prompt => {
      toolsContent += `<li><strong>${prompt}</strong></li>`;
    });
    toolsContent += '</ul>';
    document.getElementById('tools').innerHTML = toolsContent;


    let roadmapContent = '<ul>';
    finalProjectTemplate["Road Map"].forEach(prompt => {
    roadmapContent += `<li><strong>${prompt}</strong></li>`;
    });
    roadmapContent += '</ul>';
    document.getElementById('roadmap').innerHTML = roadmapContent;

    
    prompts = finalProjectTemplate["Tools and Requirements"]
    let htmlContent = '<ul>';
    prompts.forEach(prompt => {
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(prompt)}`;
        htmlContent += `<li><strong>${prompt}:</strong> <a href="${searchUrl}" target="_blank">${searchUrl}</a></li>`;
    });
    htmlContent += '</ul>';

    document.getElementById('online').innerHTML = htmlContent;
    }
    catch (error) {
      console.log("Error parsing JSON: ", error);
      window.location.href = 'jsonError.html';
      return;
    }
  }

});


function selectProject(projectNum) {
  setCookie('selectedProject', projectNum, 7);
  setCookie('projectTemplate', JSON.stringify(projectTemplatesSet[projectNum-1]), 7);

  window.location.href = 'finalProject.html';

}
function showLoadingSpinner() {
  document.getElementById('loadingOverlay').style.display = 'block';
}

function hideLoadingSpinner() {
  document.getElementById('loadingOverlay').style.display = 'none';
}



async function setProject(name, skill, languages, frameworks, interests, apiKey) {
  projectTemplates = await generateProjectTemplate(skill, languages, frameworks, interests, apiKey)
  try {
    projectTemplates = JSON.parse(projectTemplates);
  }
  catch (error) {
    console.log("Error parsing JSON: ", error);
    window.location.href = 'jsonError.html';
    return;
  }

  projectTemplates.forEach((projectTemplate, index) => {
    console.log(projectTemplate);
    const titleLocation = `#project${1 + index} .title`;
    const descriptionLocation = `#project${1 + index} .description`;

    document.querySelector(titleLocation).innerHTML = projectTemplate.Title;
    document.querySelector(descriptionLocation).innerHTML = projectTemplate["Short Description"];
    hideLoadingSpinner(); // Hide loading spinner when done

  });
  
  return projectTemplates;
}

async function generateProjectTemplate(experience, languages, frameworks, interests, apiKey) {
  const instruction = "Respond in a very strict JSON format. Provide three distinct project ideas, each as a separate JSON object in an array. Each project idea should have keys 'Title', 'Short Description' (a brief description), 'Long Description' (very long detailed description), 'Road Map' (as a list) , and 'Tools and Requirements' (as a list).";

  const prompt = `For a ${experience} programmer skilled in ${languages} and familiar with ${frameworks}, interested in ${interests}, generate three unique and innovative project ideas. Each idea should be distinct and consider incorporating emerging trends or unusual technology combinations. Format each idea as instructed.`;

  const data = {
    model: "gpt-3.5-turbo",
    messages: [{ "role": "system", "content": instruction },
               { "role": "user", "content": prompt }]
  };


  try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify(data)
      });

      if (!response.ok) {
        if(response.status === 401) {
            // Handle 401 Unauthorized error
            console.error('Unauthorized: Invalid API key');
            // Redirect or perform any other operation
            window.location.href = 'keyError.html';
            return null;
        } else {
            // Handle other HTTP errors
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    }

      const responseData = await response.json();
        
      if (responseData && responseData.choices && responseData.choices.length > 0) {
          const messages = responseData.choices[0].message;
          return messages ? messages.content : null;
      } else {
          return null;
      }
      } catch (error) {
          window.location.href = 'keyError.html';
          return null;
      }
}

function saveFormData() {
  var name = document.forms['regForm']['name'].value;
  var skill = getSelectedSkill();
  var languages = document.forms['regForm']['languages'].value;
  var frameworks = document.forms['regForm']['frameworks'].value;
  var interests = document.forms['regForm']['interests'].value;
  var apiKey = document.forms['regForm']['apiKey'].value;

  setCookie('name', name, 7);
  setCookie('skill', skill, 7);
  setCookie('languages', languages, 7);
  setCookie('frameworks', frameworks, 7);
  setCookie('interests', interests, 7);
  setCookie('apiKey', apiKey, 7);

  console.log("cookies saved");
}


function nextPage() {
  window.location.href = 'projects.html';
}

function getSelectedSkill() {
  var skillRadios = document.forms['regForm']['skill'];
  for (var i = 0; i < skillRadios.length; i++) {
      if (skillRadios[i].checked) {
          return skillRadios[i].value;
      }
  }
  return ''; // No selection
}

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function setCookie(name, value, daysToLive) {
  var date = new Date();
  date.setTime(date.getTime() + (daysToLive*24*60*60*1000));
  var expires = "expires=" + date.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/";
}


function listToFormattedString(list) {
  return list.map(item => `- ${item}`).join('<br>');
}