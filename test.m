clc;
clearvars;

groupA1 = 0; groupA2 = 0; groupA3 = 0;
groupB1 = 0; groupB2 = 0; groupB3 = 0;
groupC1 = 0; groupC2 = 0; groupC3 = 0;

A_size = input('Enter number of student in class A: ');
classA = zeros(1, A_size);

for i = 1:A_size
    classA(i) = input('Enter student score: ');
end

for i = 1:A_size
    if classA(i) < 50
        groupA1 = groupA1 + 1;
    elseif classA(i) >= 50 && classA(i) <= 75
        groupA2 = groupA2 + 1;
    elseif classA(i) > 75 && classA(i) <= 100
        groupA3 = groupA3 + 1;
    end
end

ScoreA = [groupA1, groupA2, groupA3];
averageA = mean(classA);
disp('Class A scores:');
disp(classA);
fprintf('Class A average marks = %.1f \n\n', averageA);

B_size = input('Enter number of student in class B: ');
classB = zeros(1, B_size);

for i = 1:B_size
    classB(i) = input('Enter student score: ');
end

for i = 1:B_size
    if classB(i) < 50
        groupB1 = groupB1 + 1;
    elseif classB(i) >= 50 && classB(i) <= 75
        groupB2 = groupB2 + 1;
    elseif classB(i) > 75 && classB(i) <= 100
        groupB3 = groupB3 + 1;
    end
end

ScoreB = [groupB1, groupB2, groupB3];
averageB = mean(classB);
disp('Class B scores:');
disp(classB);
fprintf('Class B average marks = %.1f \n\n', averageB);

C_size = input('Enter number of student in class C: ');
classC = zeros(1, C_size);

for i = 1:C_size
    classC(i) = input('Enter student score: ');
end

for i = 1:C_size
    if classC(i) < 50
        groupC1 = groupC1 + 1;
    elseif classC(i) >= 50 && classC(i) <= 75
        groupC2 = groupC2 + 1;
    elseif classC(i) > 75 && classC(i) <= 100
        groupC3 = groupC3 + 1;
    end
end

ScoreC = [groupC1, groupC2, groupC3];
averageC = mean(classC);
disp('Class C scores:');
disp(classC);
fprintf('Class C average marks = %.1f \n\n', averageC);

labels = {'Below 50', '50–75', 'Above 75'};

figure;

subplot(1,3,1);
pie3(ScoreA, labels);
title(sprintf('Class A Scores\nAverage: %.1f', averageA));

subplot(1,3,2);
pie3(ScoreB, labels);
title(sprintf('Class B Scores\nAverage: %.1f', averageB));

subplot(1,3,3);
pie3(ScoreC, labels);
title(sprintf('Class C Scores\nAverage: %.1f', averageC));

