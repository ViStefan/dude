#!/usr/bin/python
import sys, re

def error(token, expected = False):
    if not expected:
        print "Error in line {}: Unexpected {}".format(token[1], token[0])
    elif expected == 1:
        print "Incorrect expression in line {} around {}".format(token[1], token[0])
    else:
        print "Error in line {}: {} expected but {} given".format(token[1], expected, token[0])

    exit()

def runtimeError(msg, name = False):
    print "Runtime error{}: {}".format(" in Sub {}".format(name) if name else "", msg)
    exit()

def isName(s):
    return re.match(r'[A-Za-z][A-za-z\d]*', s) and s not in ['if', 'then', 'else', 'end']

def isNumber(s):
    return s.isdigit()


def chooseDelimeter(s):
    delimeters = ['//', ' ', '\t', '\n',    # delimeters that are not tokens
                  ';', '<', '+', '-', '*',    # rest are tokens
                  ':', '%', '=', ',', '(', ')']
    position = s.find(delimeters[0])
    result = delimeters[0]
    push = False
    comment = True
    for i in range(1, len(delimeters)):
        pos = s.find(delimeters[i])
        if position < 0:
            if pos >= 0:
                position = pos
                result = delimeters[i]
                push = i > 3
                comment = False
        else:
            if pos >= 0:
                if pos < position:
                    position = pos
                    result = delimeters[i]
                    push = i > 3
                    comment = False
    return (result, push, comment)


def getTokens(infile):
    tokens = []
    lineNum = 1
    with infile as f:
        for line in f:
            line = line.rstrip('\n').strip(' ').strip('\t');
            if len(line) > 0:
                while len(line) > 0:
                    delimeter = chooseDelimeter(line)
                    split = line.split(delimeter[0], 1)
                    token = split[0]
                    line = split[1] if len(split) > 1 and not delimeter[2] else ''
                    if len(token) > 0:
                        tokens.append((token, lineNum))
                    if delimeter[1]:
                        tokens.append((delimeter[0], lineNum))
            lineNum += 1

    return tokens[::-1]

def end(tokens):
    return len(tokens) == 0


def getArgs(tokens):
    args = []
    t = tokens.pop()
    if t[0] != 'arg': error(t, 'arg')

    t = tokens.pop()
    comma = False
    while t[0] != ';':
        comma = False
        args.append(t[0] if isName(t[0]) else error(t, 'argument name'))

        t = tokens.pop()    # TODO: bug, you can pass names without commas
        if t[0] == ',':
            t = tokens.pop()
            comma = True

    if comma: error(t, 'argument')

    return args


def getAssignment(tokens):
    var = tokens.pop()[0]

    t = tokens.pop()
    if t[0] != '=': error(t, '=')

    tree = {'_': 'as', 'v': var, 'e': getExpression(tokens)}
    
    t = tokens.pop()
    if t[0] != ';': error(t)

    return tree


def getCall(tokens):
    tree = {'f': tokens.pop()[0], 'args': []}

    t = tokens.pop()

    # really DIRTY hack
    # TODO: fix
    if tokens[len(tokens) - 1][0] == ')': t = tokens.pop()

    comma = False
    while t[0] != ')':
        comma = False
        tree['args'].append(getExpression(tokens))

        t = tokens.pop()    # TODO: bug, you can pass args without commas
        tokens.append(t)    # TODO: peek
        if t[0] in [',', ')']:
            t = tokens.pop()
        if t[0] == ',':
            comma = True

    if comma: error(t, 'call argument')

    return tree


def getExpression(tokens):
    operators = {
        '+': 0,
        '-': 0,
        '*': 1,
        ':': 1,
        '%': 1
    }

    stack = []
    expression = []
    braces = 0

    while True:
        t = tokens.pop()
        if isNumber(t[0]):
            expression.append(int(t[0]))
        elif isName(t[0]):
            c = tokens.pop() # TODO: peek
            tokens.append(c)
            if c[0] == '(':
                tokens.append(t)
                expression.append(getCall(tokens))
            else:
                expression.append(t[0])
        elif t[0] == '(':
            braces += 1
            stack.append(t[0])
        elif t[0] == ')':
            braces -= 1
            if braces < 0: break
            while len(stack) and stack[len(stack) - 1] != '(': # TODO peek
                expression.append(stack.pop())

            if not len(stack): error(t, 1) # TODO: refactor this shit
            stack.pop()
        elif t[0] in operators:
            while len(stack) and (stack[len(stack) - 1] in operators and operators[t[0]] <= operators[stack[len(stack) - 1]]):
                expression.append(stack.pop())
            stack.append(t[0])
        else:
            break

    while len(stack):
        if stack[len(stack) - 1] not in operators: error(t, 1)
        expression.append(stack.pop())

    # TODO: simplify
    tokens.append(t)
    return expression


def getTest(tokens):
    test = [getExpression(tokens)]
    t = tokens.pop()
    test.append(t[0] if t[0] in ['<', '='] else error(t, '< or ='))
    test.append(getExpression(tokens))

    return test


def getIf(tokens):
    tree = {'_': tokens.pop()[0]}
    tree['t'] = getTest(tokens)

    t = tokens.pop()
    if t[0] != 'then': error(t, 'then')

    tree['a'] = getBody(tokens)

    t = tokens.pop()
    if t[0] == 'else':
        tree['b'] = getBody(tokens)
        t = tokens.pop()

    if t[0] != 'end': error(t, 'end')

    t = tokens.pop()
    if t[0] != ';': error(t, ';')

    return tree

def getBody(tokens):
    body = []
    while True:
        t = tokens.pop() # TODO: peek
        tokens.append(t)

        if t[0] == 'if':
            body.append(getIf(tokens))
        elif isName(t[0]):
            body.append(getAssignment(tokens))
        else:
            return body

def getSub(tree, tokens):
    t = tokens.pop()
    main = t[0] == 'Alg' if t[0] in ['Sub', 'Alg'] else error(t, 'Sub or Alg')

    t = tokens.pop()
    name = t[0] if isName(t[0]) else error(t, 'Sub name')

    t = tokens.pop()
    if t[0] != ';': error(t, ';')

    tree[name] = {}
    tree[name]['main'] = main
    tree[name]['args'] = getArgs(tokens)
    tree[name]['body'] = getBody(tokens)

    t = tokens.pop()
    if t[0] != 'end': error(t, 'end')

    t = tokens.pop()
    if t[0] != ';': error(t, ';')

    return main


def getTree(tokens):
    tree = {}
    while not end(tokens):
        getSub(tree, tokens)

    return tree

def evalExpression(ast, expression, variables):
    stack = []
    for t in expression:
        if type(t) is int:
            stack.append(t)
        elif type(t) is str:
            if t in '+-*:%':
                b = stack.pop()
                a = stack.pop()
                if t == '+':
                    stack.append(a + b)
                elif t == '-':
                    stack.append(a - b)
                elif t == '*':
                    stack.append(a * b)
                elif t == ':':
                    stack.append(a / b)
                elif t == '%':
                    stack.append(a % b)
            elif t in variables:
                stack.append(variables[t])
            else:
                runtimeError('Unknown variable {}'.format(t))
        elif type(t) is dict:
            stack.append(call(ast, t['f'], t['args'], variables))

    # and what to do here (relevant to line 114)
    return stack.pop()


def evalTest(ast, test, variables):
    if test[1] == '<':
        return evalExpression(ast, test[0], variables) < evalExpression(ast, test[2], variables)
    elif test[1] == '=':
        return evalExpression(ast, test[0], variables) == evalExpression(ast, test[2], variables)


def execute(ast, statement, variables):
    if type(statement) is list:
        for stat in statement:
            execute(ast, stat, variables)
    elif statement['_'] == 'if':
        if evalTest(ast, statement['t'], variables):
            execute(ast, statement['a'], variables)
        elif 'b' in statement:
            execute(ast, statement['b'], variables)
    elif statement['_'] == 'as':
        variables[statement['v']] = evalExpression(ast, statement['e'], variables)


def call(ast, name, args, context = {}):
    if name not in ast: runtimeError('Call to undefined sub', name)
    sub = ast[name]

    if len(args) != len(sub['args']):
        runtimeError('Sub takes {} arguments but {} given'.format(len(sub['args']), len(args)), name)

    variables = {}
    for i in range(len(sub['args'])):
        variables[sub['args'][i]] = evalExpression(ast, args[i], context)
    variables[name] = 0

    for statement in sub['body']:
        execute(ast, statement, variables)

    return variables[name]


def interpret(ast, args, name = False):
    if not name:
        for sub in ast:
            if ast[sub]['main']:
                return call(ast, sub, args)
        runtimeError('Alg not found')
    else:        
        return call(ast, name, args)


def init():
    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')
        args = sys.argv[2:]
    else:
        infile = sys.stdin
        args = sys.argv[1:]

    args = [[int(x)] for x in args]

    print interpret(getTree(getTokens(infile)), args)

init()
