close all
clear
% Nested functions not allowed but compound statements ok
function outer
  a = 0
  b = 1
  if a == 0
    b = 2
  end

end
