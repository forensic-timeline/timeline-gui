// import * as Plot from "@observablehq/plot";
import {h} from "vue";

export default {
  props: {
    options: Object
  },
  render() {
    return Plot.plot({
      ...this.options,
      document: new Document()
    }).toHyperScript();
  }
};