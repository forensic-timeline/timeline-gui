<script setup>
import * as Plot from "@observablehq/plot"
import { ref, onMounted } from 'vue'

const pElementRef = ref(null)

// Observable test

var height = 200
var tickHeight = 25
var fontSizeInt = 16
var sideMargins = 70
var width = 1000
var lineLength = 15

function wrapText(inputString, segmentLength) {
  const words = inputString.split(" ");
  let result = "";
  let currentLineLength = 0;
  let numberOfLines = 0;

  for (const word of words) {
    if (currentLineLength + word.length + 1 <= segmentLength) {
      // Add the word and a space to the current line
      result += (result === "" ? "" : " ") + word;
      currentLineLength += word.length + 1;
    } else {
      // Start a new line with the word
      result += "\n" + word;
      currentLineLength = word.length;
      numberOfLines++;
    }
  }

  // Count the last line
  if (result !== "") {
    numberOfLines++;
  }

  return {
    text: result,
    numberOfLines: numberOfLines
  };
}

var data = [
    {
        year: 1788,
        composition: `Symphony No. 41 "Jupiter"`,
        composer: "Wolfgang Amadeus Mozart",
        link: "https://en.wikipedia.org/wiki/Symphony_No._41_(Mozart)"
    },
    {
        year: 1894,
        composition: "Prelude to the Afternoon of a Faun",
        composer: "Claude Debussy",
        link: "https://en.wikipedia.org/wiki/Pr%C3%A9lude_%C3%A0_l%27apr%C3%A8s-midi_d%27un_faune"
    },
    {
        year: 1805,
        composition: `Symphony No. 3 "Eroica"`,
        composer: "Ludwig van Beethoven",
        link: "https://en.wikipedia.org/wiki/Symphony_No._3_(Beethoven)"
    },
    {
        year: 1913,
        composition: "Rite of Spring",
        composer: "Igor Stravinsky",
        link: "https://en.wikipedia.org/wiki/The_Rite_of_Spring"
    },
    {
        year: 1741,
        composition: "Goldberg Variations",
        composer: "Johann Sebastian Bach",
        link: "https://en.wikipedia.org/wiki/Goldberg_Variations"
    },
    {
        year: 1881,
        composition: "Piano Concerto No. 2",
        composer: "Johannes Brahms",
        link: "https://en.wikipedia.org/wiki/Piano_Concerto_No._2_(Brahms)"
    },
    {
        year: 1826,
        composition: `A Midsummer Night's Dream "Overture"`,
        composer: "Felix Mendelssohn",
        link: "https://en.wikipedia.org/wiki/A_Midsummer_Night%27s_Dream_(Mendelssohn)"
    }
]
var preparedData = data
  .map(function (d) {
    const composerShort = d.composer.split(" ").slice(-1);
    const { text, numberOfLines } = wrapText(
      `${d.composition} (${composerShort})`,
      lineLength
    );
    return { ...d, text, numberOfLines };
  })
preparedData.sort(function (a, b) { return a.year - b.year })

onMounted(() => {
    pElementRef.value.append(Plot.plot({
        style: {
            fontSize: fontSizeInt + "px"
        },
        width,
        height,
        marginLeft: sideMargins,
        marginRight: sideMargins,
        x: { axis: null },
        y: { axis: null, domain: [-height / 2, height / 2] },
        marks: [
            Plot.ruleY([0]),
            Plot.ruleX(preparedData, {
                x: "year",
                y: (d, i) => (i % 2 === 0 ? tickHeight : -tickHeight)
            }),
            Plot.dot(preparedData, { x: "year", fill: "#fff", stroke: "#000" }),
            Plot.text(preparedData, {
                x: "year",
                y: (d, i) => (i % 2 === 0 ? -fontSizeInt / 2 - 4 : fontSizeInt / 2 + 4),
                text: (d) => d.year.toString()
            }),
            Plot.text(preparedData, {
                x: "year",
                y: (d, i) =>
                    i % 2 === 0
                        ? tickHeight + d.numberOfLines * fontSizeInt * 0.5
                        : -tickHeight - d.numberOfLines * fontSizeInt * 0.5,
                text: "text"
            })
        ]
    }))
})
</script>

<template>
    <div ref="pElementRef">Hello</div>
</template>