function getProtoChain() {
  const protoChain = [this];   
  let proto = this;
  while (true) {
    const next = proto.__proto__;
    if (protoChain.includes(next)) {
      return protochain;
    }
    if (next === null) {
      break;
    }
    protoChain.push(next)
    proto = next;
  }
  protoChain.reverse();
  return protoChain;
}

Object.super = function(f, attr) {
  if (!attr) {
    attr = f.name;
  }
  const protoFuncs = getProtoChain(this).map((proto) => {
    return [proto, proto[attr]];
  });

  let prev = null;
  let current = null;
  for (const protoFunc of protoFuncs) {
    current = 
  }
  return superFunc.bind(this);
}

Object.extend = function(child) {
  if (child === null || child === undefined) {
    child = {};
  }
  child.__proto__ = this;
  return child;
}

Object.new = function(child) {
  const instance = this.extend(child);
  if (instance.__init__) {
    instance.__init__(); 
  }
}
