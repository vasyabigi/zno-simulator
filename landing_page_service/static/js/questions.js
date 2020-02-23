var app = new Vue({
    el: '#app',
    data: {
        id: 526,
        content: "Не мають закінчення обидва слова в рядку",
        choices: [
            { id: 0, content: "А: ухвалено, збудований", is_correct: false },
            { id: 1, content: "Б: сорок, по-полтавськи", is_correct: false },
            { id: 2, content: "В: горілиць, плакучі", is_correct: false },
            { id: 3, content: "Г: запанібрата, змито", is_correct: true }],

        answer: null
    },
    mounted() {
      axios.get("http://zno-dev.eu-central-1.elasticbeanstalk.com/questions/random?subject=ukr&format=raw")
      .then(response => {this.id = response.data.id,
                         this.content = response.data.content,
                         this.choices = response.data.choices,
                         this.answer = null                            
                        }
            )
    }
})