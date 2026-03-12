import data from "./node_modules/@nationalarchives/frontend/config/stylelint.config.js";

data.ignoreFiles = ["app/**/*.css"];
data.rules = {
  ...data.rules,
  "scss/no-global-function-names": null,
  "no-duplicate-selectors": null,
  "order/properties-order": null,
  "scss/at-rule-no-unknown": true,
};

export default data;
