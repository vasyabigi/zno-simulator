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

        answer: null,
    },
})
