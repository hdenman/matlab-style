close all
clear
% Nested functions not allowed
function outer
  a = 0
  b = 1
  if a == 0
    b = 2
  end

  function inner
  end

end
