const BACKEND = 'http://0.0.0.0:9001';

const assets = [
  'laughing-1.svg', // nicest
  'smile.svg',
  'sceptic.svg',
  'confused-3.svg',
  'angry-2.svg',
  'sad-1.svg'  // most toxic
];

// function to scale the number of assets into a domain of (0,1)
const scaler = (domain, range) => n => {
  const [minD, maxD] = domain;
  const [minR, maxR] = range;
  if (minD <= maxD) {
    if (n <= minD) return minR;
    if (n >= maxD) return maxR;
  } else {
    if (n >= minD) return minR;
    if (n <= maxD) return maxR;
  }
  return (maxR - minR) * ((n - minD) / (maxD - minD)) + minR;
};

const scale = scaler([0, 1], [0, assets.length]); // (domain, range)

// this function selects an asset based on the scale value
const selectAsset = toxicity => {
    // We'll use Math.floor to confirm it's an integer
    // below the maximum (aka not beyond the array)
    // this can also be achieved by setting the output range to
    // be [0, assets.length - 1]
    const assetIdx = Math.floor(scale(toxicity));
    return assets[assetIdx];
}

const debounceOnKeydown = function(ele, timeout, cb) {
  ele.addEventListener('keydown', function() {
    if (this.timeoutId) {
      // Clear existing timeout
      window.clearTimeout(this.timeoutId);
    }
    this.timeoutId = window.setTimeout(function() {
      cb(this);
    }, timeout);
  });
}

const makeRequest = function(path, data) {
    const url = BACKEND + path;
    return fetch(url, {
      method: 'POST',
      body: JSON.stringify({q: data}),
      headers: new Headers({
        'Content-Type': 'application/json'
      })
  }).then(resp => resp.json());
}

const onLoad = function() {
    // Set up our application to run here
    console.log('Page loaded');
    const ele = document.querySelector('textarea');
    const img = document.querySelector('img');
    const initialIcon = img.src;
    let prevText;
    // Do stuff
    debounceOnKeydown(ele, 500, function(that) {
      const text = ele.value;
      console.log('Event ->', text);
      if (text === '') {
        img.src = initialIcon;
      } else if (text !== prevText) {
        // Make request
        makeRequest('/predict', text).then(json => {
          if (json.status === 'ok') {
            // We have a toxicity
            const toxicity = Number(json['toxicity']);
            const asset = selectAsset(toxicity);
            img.src = `assets/${asset}`;
          } else {
            console.log(resp.error);
          }
        });
      }
      prevText = text;

    });

}
document.addEventListener('DOMContentLoaded', onLoad);

